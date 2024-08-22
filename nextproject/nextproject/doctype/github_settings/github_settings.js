// Copyright (c) 2023, Dexciss and contributors
// For license information, please see license.txt

frappe.ui.form.on('Github Settings', {
	refresh: function(frm) {
		frm.add_custom_button(__('Update Latest Changes'),function(){
			get_repo_name(frm);
	}).addClass("btn-primary");
	
	
	let get_repo_name = function(frm){
		const username = frm.doc.username
		const passd = frm.doc.password
		const perPage = 100;
        let page = 1;
        let allRepositories = [];
      
        const fetchRepositories = async () => {
          const url = `https://api.github.com/user/repos?per_page=${perPage}&page=${page}`;
          const response = await fetch(url, {
            headers: {
              'Authorization': 'Bearer'+' '+passd,
              'Accept': 'application/vnd.github.v3+json'
            }
          });
      
          if (!response.ok) {
            throw new Error(`Failed to fetch data. Status code: ${response.status}`);
          }
      
          const repositories = await response.json();
          return repositories;
        };
      
        const fetchAllPages = async () => {
          try {
            const repositories = await fetchRepositories();
            if (repositories.length > 0) {
              allRepositories = allRepositories.concat(repositories);
              page++;
              await fetchAllPages(); // Fetch the next page
            }
          } catch (error) {
            console.error(`Request Exception: ${error}`);
          }
        };
      
        return fetchAllPages()
          .then(() => {
            // const repositoryNames = allRepositories.map((repo) => {repo.name});
            const repositoryNames=[]
            for (let repo of allRepositories){
              let rep_name= repo.name
              let url= repo.html_url
              repositoryNames.push({
                "repo":rep_name,"url":url
              })
            }
			if (repositoryNames)
        {
        frappe.call({
          method:"update_latest_code",
					doc: frm.doc,
					args:{
						"repo_list":repositoryNames
					},
					callback:function(r)
          {
						if (r.message)
              {
							  frm.refresh()
						  }
            }
				      })
			    }
            return repositoryNames;
          })
          .catch(error => {
            console.error(`Request Exception: ${error}`);
            return [];
          });
	}}
});
