// Copyright (c) 2021, Dexciss and contributors
// For license information, please see license.txt
let username = ''
let password = ''
frappe.ui.form.on('Test Session', {
	onload: function(frm){
		frm.set_df_property("product_version","placeholder","example: v1.0.5");
		frm.set_df_property("release_title", "placeholder", "Version 1.0.5");
	},
	setup:function(frm){
		frm.set_query("test_case", "test_cases", function() {
			return {
				filters: {
					"project": frm.doc.project,
				}
			}
		});
		frm.set_query("task", function() {
			return {
				filters: {
					"project": frm.doc.project,
				}
			}
		});
	},
	refresh: function(frm) {
		if (frm.doc.docstatus == '1' && frm.doc.overall_status == 'PASS' && !frm.doc.git_released)
			{
		frm.add_custom_button(__('Git Release'),
			function(){
				if (!frm.doc.product){
					frappe.throw("Product is mandatory for 'Git Release'")
				}
				if (!frm.doc.product_version){
					frappe.throw("Tags is mandatory for 'Git Release'")
				}
				if (!frm.doc.release_title){
					frappe.throw("Release Title is mandatory for 'Git Release'")
				}
				frappe.call({
					method:"git_release",
					doc: frm.doc,
					callback:function(r){
						if (r.message){
							frm.refresh_field('git_released');
							frm.refresh()
						}
					}
				})
			}).addClass("btn-primary");
			}
		if(frm.doc.pull_request == '0')
		{
			frm.add_custom_button(__('Create Pull Request'),
				function(){
					if (!frm.doc.product){
						frappe.throw("Product is mandatory for 'Create Pull Request'")
					}
					if (!frm.doc.base_branch){
						frappe.throw("Base Branch is mandatory for 'Create Pull Request'")
					}
					if (!frm.doc.head_branch){
						frappe.throw("Head Branch is mandatory for 'Create Pull Request'")
					}
					if (!frm.doc.pull_request_title){
						frappe.throw("Pull Request Title is mandatory for 'Create Pull Request'")
					}
					frappe.call({
						method:"create_pull_request",
						doc: frm.doc,
						callback:function(r){
							frm.refresh_field('pull_request');
							cur_frm.reload_doc();
						}
					})
					
				}).addClass("btn-primary");
		}			
		if (frm.doc.git_released)
		{
			frm.toggle_enable('*', false);
		}
		frappe.db.get_single_value("Github Settings", "username").then((value) => {
			if (value){
				username = value
			}
		});
		frappe.db.get_single_value("Github Settings", "password").then((valuee) => {
			if (valuee){
				password = valuee
			}
		});
		if(frm.doc.project){
			frm.set_query("test_case", "test_cases", function() {
				return {
					filters: {
						"project": frm.doc.project,
					}
				}
			});
		}
		if(frm.doc.project){
			frm.set_query("task", function() {
				return {
					filters: {
						"project": frm.doc.project,
					}
				}
			});
		}
	},
	product: function(frm){
		if (frm.doc.product)
		{
			let owner = username
			let passd = password
			let repository = frm.doc.product
			getTagsForRepository(owner, repository)
			function getTagsForRepository(owner, repository) {
				const urlTags = `https://api.github.com/repos/${owner}/${repository}/tags`;
		
				return fetch(urlTags, {
					headers: {
						'Authorization': 'Bearer'+' '+passd,
						'Accept': 'application/vnd.github.v3+json'
					}
				})
				.then(response => {
					if (response.ok) {
						return response.json();
					}
					frappe.msgprint('Tags not found')
					throw new Error(`Failed to fetch tags. Status code: ${response.status}`);
				})
				.then(tags => {
					let availableTags = tags.map(tag => tag.name).join('\n');
					if (availableTags)
					{
						frm.set_value('tags', availableTags);
						frm.refresh_field('tags');
					}
				})
				.catch(error => {
					frm.set_value('tags', '');
					frm.refresh_field('tags');
					return [];
				});
			}
		}
		else
		{
			frm.set_value('tags', '');
			frm.refresh_field('tags');
		}
	}
});