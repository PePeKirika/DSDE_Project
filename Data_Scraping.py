import requests
import json
import os

search_base_url = "https://api.elsevier.com/content/search/scopus"
abstract_doi_url = "https://api.elsevier.com/content/abstract/doi/"
abstract_scopus_url = "https://api.elsevier.com/content/abstract/scopus_id/"
abstract_eid_url = "https://api.elsevier.com/content/abstract/eid/"

api_key = "01d58db39c61dd0939ce840a1321fbc0"

search_query = "TITLE-ABS-KEY(chulalongkorn) AND (PUBYEAR < 2018 OR PUBYEAR > 2023)"

headers = {
    "X-ELS-APIKey": api_key,
    "Accept": "application/json"
}

search_params = {
    "query": search_query,
    "count": 1,
}

output_folder = "./Raw_data/Additional_Data"
os.makedirs(output_folder, exist_ok=True)

# Maximum number of results to fetch
max_results = 1000  # Adjust as needed
total_results = 0
travelled = 0

while total_results < max_results:
    search_params['start'] = travelled 
    
    search_response = requests.get(search_base_url, headers=headers, params=search_params)
    
    if search_response.status_code == 200:
        search_data = search_response.json()
        entries = search_data.get("search-results", {}).get("entry", [])
        
        if not entries:
            print(f"No more articles found after {total_results} results.")
            break
        
        result = entries[0] 
        doi = result.get("prism:doi")
        scopus_id = result.get("dc:identifier")
        eid = result.get("eid")
        
        if doi:
            abstract_url = f"{abstract_doi_url}{doi}"
            abstract_response = requests.get(abstract_url, headers=headers)
            
            if abstract_response.status_code == 200:
                article_data = abstract_response.json()
                
                file_path = os.path.join(output_folder, f"article_{travelled + 1}.json")
                with open(file_path, "w", encoding="utf-8") as json_file:
                    json.dump(article_data, json_file, ensure_ascii=False, indent=4)
                    
                total_results += 1
            else:
                print(f"Failed to retrieve metadata for DOI {doi}: {abstract_response.status_code}")
                
        elif scopus_id:
            abstract_url = f"{abstract_scopus_url}{scopus_id}"
            abstract_response = requests.get(abstract_url, headers=headers)
            
            if abstract_response.status_code == 200:
                article_data = abstract_response.json()
                
                file_path = os.path.join(output_folder, f"article_{travelled + 1}.json")
                with open(file_path, "w", encoding="utf-8") as json_file:
                    json.dump(article_data, json_file, ensure_ascii=False, indent=4)
                    
                total_results += 1
            else:
                print(f"Failed to retrieve metadata for Scopus ID {scopus_id}: {abstract_response.status_code}")
        elif eid:
            abstract_url = f"{abstract_eid_url}{eid}"
            abstract_response = requests.get(abstract_url, headers=headers)
            
            if abstract_response.status_code == 200:
                article_data = abstract_response.json()
                
                file_path = os.path.join(output_folder, f"article_{travelled + 1}.json")
                with open(file_path, "w", encoding="utf-8") as json_file:
                    json.dump(article_data, json_file, ensure_ascii=False, indent=4)
                    
                total_results += 1
            else:
                print(f"Failed to retrieve metadata for EID {eid}: {abstract_response.status_code}")
        else:
            print(f"No DOI found for article {travelled + 1}. Skipping.")
    else:
        print(f"Failed to retrieve data for article {travelled + 1}: {search_response.status_code}")
        break
    travelled += 1

print(f"All data has been saved to the '{output_folder}' folder. Fetched a total of {total_results} articles.")
