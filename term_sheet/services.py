import requests
import os
import json
from .models import Pipeline,TermSheet, PipelineStage,PreApprovalSheet
from django.conf import settings
from core.services import OAuthServices
from core.models import OAuthToken


LIMIT_PER_PAGE = 100
BASE_URL = 'https://services.leadconnectorhq.com'
API_VERSION = "2021-07-28"

class PipeLinesError(Exception):
    "exeption for pipeline"
    pass

class OpportunityError(Exception):
    "exeption for pipeline"
    pass


class PipelineServices:
    
    @staticmethod
    def get_pipelines(query=None):
        
        url = f"{BASE_URL}/opportunities/pipelines"
        token_obj = OAuthServices.get_valid_access_token_obj()
        headers = {
            "Authorization": f"Bearer {token_obj.access_token}",
            "Content-Type": "application/json",
            "Version": API_VERSION,
        }
        params = {
            "locationId": token_obj.LocationId
        }
        response = requests.get(url, headers=headers, params=params)
        print(response.status_code)
        if response.status_code == 200:
            
            #for debug
            # print(json.dumps( response.json().get("pipelines", []),indent=4))
            # with open(os.path.join(settings.BASE_DIR,"pipelines.json"), "w") as file:
            #     file.write(json.dumps( response.json().get("pipelines", []),indent=4))
            
            return response.json().get("pipelines",[])
        else:
            raise PipeLinesError(f"Faile to fetch pipelines: {response.json().get('pipelines',[])}")
    
    @staticmethod
    def pull_pipelines():
        """Fetches pipelines from GHL and stores them in the local database"""
        location_ids = OAuthToken.objects.values_list('LocationId', flat=True)
        for location_id in location_ids:
            pipelines = PipelineServices.get_pipelines(location_id)

            if not pipelines:
                print("No pipelines found or API request failed.")
                return
            
            for pipeline_data in pipelines:
                ghl_id = pipeline_data.get("id")
                name = pipeline_data.get("name")
                LocationId = location_id
                
                if ghl_id and name:

                    pipeline, created = Pipeline.objects.update_or_create(
                        ghl_id=ghl_id,
                        defaults={"name": name,"LocationId":LocationId}
                    )
                    if created:
                        print(f"Pipeline '{name}' added.")
                    else:
                        print(f"Pipeline '{name}' updated.")
                    
                    stages = pipeline_data.get("stages", [])
                    for stage_data in stages:
                        stage_ghl_id = stage_data.get("id")
                        stage_name = stage_data.get("name")
                        position = stage_data.get("position")

                        # Create or update the pipeline stage
                        if stage_ghl_id and stage_name is not None and position is not None:
                            pipeline_stage, stage_created = PipelineStage.objects.update_or_create(
                                id=stage_ghl_id,  # Using the stage id as primary key
                                pipeline=pipeline,
                                defaults={"name": stage_name, "position": position}
                            )
                            if stage_created:
                                print(f"Stage '{stage_name}' for pipeline '{name}' added.")
                            else:
                                print(f"Stage '{stage_name}' for pipeline '{name}' updated.")
               

class OpportunityServices:
    
    @staticmethod
    def get_opportunity(url=None, location_id=None,query :dict =None, limit=LIMIT_PER_PAGE):
        '''
        Fetch opportunities
        '''
        print(location_id)
        token_obj = OAuthServices.get_valid_access_token_obj()
        
        headers = {
            "Authorization": f"Bearer {token_obj.access_token}",
            "Content-Type": "application/json",
            "Version": API_VERSION,
        }
        params ={
            'limit':limit,
            'location_id':token_obj.LocationId
        }
        if url:
            req_url = url
        else:
            req_url = f"{BASE_URL}/opportunities/search"
        if query:
            params.update(query)
        response = requests.get(req_url, headers=headers, params=params)
        if response.status_code == 200:
            with open(os.path.join(settings.BASE_DIR,"opp_response.json"),"a") as file:
                file.write(json.dumps(response.json().get("opportunities",[]), indent=4))
            
            # return response.json().get("opportunities",[])
            # res = dict(filter(lambda res : res[0]!= "opportunities",response.json().items()))
            with open(os.path.join(settings.BASE_DIR,"opp_filter.json"),"a") as file:
                file.write(json.dumps(response.json().get("meta",[]),indent=4))
                file.write(json.dumps(params,indent=4))
          
            return response.json().get("opportunities", []),response.json().get("meta",[])
        else:
            
            print(f"Opportunity service Error: {json.dumps(response.json(), indent=4)}")
            return None,None
    
    
    @staticmethod
    def upload_pdf(term_sheet:TermSheet, custom_field_id):
        '''
        Upload a PDF file to GoHighLevel
        '''
        if not term_sheet.pdf_file:
            print("Error: No PDF file associated with this TermSheet.")
            return None
        
        token_obj = OAuthServices.get_valid_access_token_obj()
        url = f"{BASE_URL}/locations/{token_obj.LocationId}/customFields/upload"
        headers = {
            "Authorization": f"Bearer {token_obj.access_token}",
            "Version": API_VERSION,
            "Accept": "application/json, text/plain, */*"
        }
        payload = {"id": custom_field_id, "maxFiles": "undefined"}
        
        with term_sheet.pdf_file.open("rb") as pdf_file:
            files = {"file": (term_sheet.pdf_file.name, pdf_file, "application/pdf")}
            response = requests.post(url, headers=headers, files=files, data=payload)
        
        if response.status_code in [200, 201]:
            response_data = response.json()
            print("PDF successfully uploaded to GoHighLevel.")
            return response_data
        else:
            print(f"Failed to upload PDF: {response.status_code} - {response.text}")
            return None

    @staticmethod
    def update_opportunity_with_pdf(opportunity_id, uploaded_file_response, custom_field_id):
        '''
        Update an opportunity in GHL with the uploaded PDF details.
        '''
        token_obj = OAuthServices.get_valid_access_token_obj()
        url = f"{BASE_URL}/opportunities/{opportunity_id}"
        headers = {
            "Authorization": f"Bearer {token_obj.access_token}",
            "Content-Type": "application/json",
            "Version": API_VERSION,
        }
        
        if not uploaded_file_response:
            print("No uploaded file response provided.")
            return None
        
        meta_data = uploaded_file_response.get("meta", [])[0]
        if not meta_data:
            print("Uploaded file metadata missing.")
            return None
        
        file_payload = {
            "customFields": [
                {
                    "id": custom_field_id,
                    "field_value": [
                        {
                            "url": meta_data.get("url"),
                            "meta": {
                                "mimetype": meta_data.get("mimetype"),
                                "name": meta_data.get("originalname"),
                                "size": meta_data.get("size")
                            },
                            "deleted": False
                        }
                    ]
                }
            ]
        }
        
        response = requests.put(url, headers=headers, json=file_payload)
        
        if response.status_code == 200:
            print(f"Successfully updated Opportunity {opportunity_id} with PDF details.")
            return response.json()
        else:
            print(f"Failed to update Opportunity {opportunity_id}: {response.text}")
            return None


    

class PreApproveServices:
    
    @staticmethod
    def upload_pdf(preapprove_sheet :PreApprovalSheet, custom_field_id):
        '''
        Upload a PDF file to GoHighLevel
        '''
        if not preapprove_sheet.pdf_file:
            print("Error: No PDF file associated with this TermSheet.")
            return None
        
        token_obj = OAuthServices.get_valid_access_token_obj()
        url = f"{BASE_URL}/locations/{token_obj.LocationId}/customFields/upload"
        headers = {
            "Authorization": f"Bearer {token_obj.access_token}",
            "Version": API_VERSION,
            "Accept": "application/json, text/plain, */*"
        }
        payload = {"id": custom_field_id, "maxFiles": "undefined"}
        
        with preapprove_sheet.pdf_file.open("rb") as pdf_file:
            files = {"file": (preapprove_sheet.pdf_file.name, pdf_file, "application/pdf")}
            response = requests.post(url, headers=headers, files=files, data=payload)
        
        if response.status_code in [200, 201]:
            response_data = response.json()
            print("PDF successfully uploaded to GoHighLevel.")
            return response_data
        else:
            print(f"Failed to upload PDF: {response.status_code} - {response.text}")
            return None











# git new opporttunity:
# class OpportunityServices:
    
#     @staticmethod
#     def get_opportunity(_,url=None,query :dict =None, limit=LIMIT_PER_PAGE):
#         '''
#         Fetch opportunities
#         '''
#         token_obj = OAuthServices.get_valid_access_token_obj()
        
#         headers = {
#             "Authorization": f"Bearer {token_obj.access_token}",
#             "Content-Type": "application/json",
#             "Version": API_VERSION,
#         }
#         params ={
#             'limit':limit,
#             'location_id':token_obj.LocationId
#         }
#         if url:
#             req_url = url
#         else:
#             req_url = f"{BASE_URL}/opportunities/search"
#         if query:
#             params.update(query)
#         response = requests.get(req_url, headers=headers, params=params)
#         if response.status_code == 200:
#             # with open(os.path.join(settings.BASE_DIR,"opp_response.json"),"a") as file:
#             #     file.write(json.dumps(response.json().get("opportunities",[]), indent=4))
            
#             # return response.json().get("opportunities",[])
#             # res = dict(filter(lambda res : res[0]!= "opportunities",response.json().items()))
#             # with open(os.path.join(settings.BASE_DIR,"opp_filter.json"),"a") as file:
#             #     file.write(json.dumps(response.json().get("meta",[]),indent=4))
#             #     file.write(json.dumps(params,indent=4))
          
#             return response.json().get("opportunities", []),response.json().get("meta",[])
#         else:
            
#             print(f"Opportunity service Error: {json.dumps(response.json(), indent=4)}")
#             return None,None
    
#     @staticmethod
#     def pull_opportunities():
#         location_ids = OAuthToken.objects.values_list('LocationId', flat=True)
#         for location_id in location_ids:
#             pass