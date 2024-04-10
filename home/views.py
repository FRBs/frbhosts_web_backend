from django.shortcuts import render,HttpResponse
from django.http import JsonResponse
import requests 
from django.views.decorators.csrf import csrf_exempt
import json
import re
from django.views.decorators.cache import cache_page
repo_name = "https://api.github.com/repos/FRBs/FRB/contents/frb/data/Galaxies"

def home(request):
    return HttpResponse('Home Page')


def send_request(url):
    headers={
        "Accept": 'application/json',
        'Content-Type': 'application/json',
        }
    res = requests.get(url=url, headers= headers)
    if res.status_code == 200:
        return res
    return False


@csrf_exempt
def get_github_json(request):
    def get_repo_directories():
        url = repo_name
        res = requests.get(url = url)
        catlog_folders = res.json()['payload']['tree']
        catlog_filenames = []
        for folder in catlog_folders['items']:
            if folder['contentType'] == 'directory':
                catlog_filenames.append(folder['name'])
        return catlog_filenames

    def list_json_files_from_repo(file):
        res = requests.get(url=f"{repo_name}/{file}").json()
        file_data = res['payload']['tree']['items']
        print(file_data)
        file_dict = {}
        for idx in range(len(file_data)):
            if file_data[idx]['contentType'] == 'file':

                if file_data[idx]['name'].find('json') >= 0:
                    file_dict.update({'file_name':file_data[idx]['name'], "file_path":file_data[idx]['path']})

                if file_data[idx]['name'].find('png') >= 0:
                    file_dict.update({"img_file_path":file_data[idx]['path']})

        return file_dict

    def extract_jsondata(file):
        file_name = list_json_files_from_repo(file)
        # print(file_name)
        try:
            if file_name['file_path'].find(file) >= 0:
                url = f"https://raw.githubusercontent.com/FRBs/FRB/main/frb/data/Galaxies/{file}/{file_name['file_name']}"
                res = send_request(url)
                if res:
                    data = res.json()
                    context = ""
                    try:
                        for idx in data['photom']:
                            if idx in ["Pan-STARRS_r"]:
                                context = data["photom"][idx]
                            else:
                                if idx.find("_r:'") >=0:
                                    context = data['photom'][idx] 
                                # else:
                                #     if idx.find("_r_") >0:
                                #         context = data['photom'][idx] 
                    except:
                        pass
                    
                    try:
                        imagePath = "https://github.com/FRBs/FRB/blob/main/"+file_name['img_file_path']
                    except:
                        imagePath = ""

                    datadict = {
                        "FRB":data['FRB'],
                        "Host R.A.":data["ra"],
                        "Host Decl.":data["dec"],
                        # "$z$":data["redshift"]["z"],
                        "$m_r$.":context,
                        "Redshift":data["redshift"]["z"],
                        "Offset ($\arcsec$)":data["offsets"]['ang_avg'],
                        "$M_*$ ($\rm M_{\odot}$)":data["derived"]["Mstar"],
                        "SFR ($\rm M_{\odot}$\yr)":data["derived"]['SFR_SED'],
                        "$Z_{\rm gas}$ ($Z_{\odot}$)":data["derived"]["Z_gas"],
                        "$t_{m}$ (Gyr)":data["derived"]["age_mass"],
                        "image_path":imagePath
                    }
                    return datadict
        
        except:
            return None

    files = get_repo_directories()
    catlogs_data = []
    for file in files[:10]:
        res = extract_jsondata(file)
        if res:
            catlogs_data.append(res)
    return JsonResponse(catlogs_data,safe=False)













