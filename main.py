import json  #developer mode
from pathlib import Path
import requests
from clint.textui import progress

class Udemy_Downloader():
    def __init__(self,token=None):
        # '''create token and header'''
        # self.token = token
        # self.header={
        # "Cookie":f"access_token={self.token}"
        # }
        pass

    def __header_creator(self,token):
        '''create token and header'''
        self.token = token
        self.header={
        "Cookie":f"access_token={self.token}"
        }

    def set_accesstoken(self):
        '''input access token'''
        self.access_token=input("pls give token / lütfen access token değerini giriniz : ")
        # self.access_token='XXXXXXXXXXXXXXXXXXXXXX'
        self.token=self.access_token
        self.__create_session()
        self.__header_creator(self.token)
        

        # return self.access_token

    def __create_session(self):
        '''create session'''
        self.session=requests.Session()

    def __get_my_course_list(self):
        url="https://www.udemy.com/api-2.0/users/me/subscribed-courses?page_size=1000"
        self.response=self.session.get(url,headers=self.header)
        self.my_course_list_status=self.response
        self.my_course_list_json_data=self.response.json()
        return self.my_course_list_status,self.my_course_list_json_data


    def list_my_course(self):
        status,data=self.__get_my_course_list()
        # status=self.my_course_list_status
        # data=self.my_course_list_json_data
        print(status.status_code)
        if status.status_code==200:
            self.course_list=data["results"]
            # course_list=data["results"]
            print(f"you have {len(self.course_list)} course... / {len(self.course_list)} kursunuz mevcut...")
            i=1
            for course in self.course_list:
                course_title=course["title"]
                # course_id=course_id_getter(course) #developer mode
                # print(i,f">> {course_title}  {course_id}") #developer mode
                print(i,f">> {course_title}  ")
                i+=1
        else:
            print("error, cant get course list / hata, kurs listesi alınamadı")

    def __get_course_title_and_id(self,chs):
        if chs>0:
            course=self.course_list[chs-1]
            course_id=course['id']
            course_title=course['title']
        return course_id,course_title

    def __get_course_chapter_and_lecture(self,course_id):
        # self.course_id,self.course_title=self.__get_course_title_and_id(choose)
        url = f"https://www.udemy.com/api-2.0/courses/{course_id}/cached-subscriber-curriculum-items/?page_size=1400"
        response=self.session.get(url,headers=self.header)
        response_json=response.json()
        results=response_json["results"]
        return response,results

    def __main_folder_creator(self,title):
        title="".join("" if c in "\/:*?\"<>|!." else c for c in  title )
        folder_name=Path(f'{title}')
        Path.mkdir(folder_name,parents=True,exist_ok=True)
        return folder_name

    def __sub_folder_creator(self,main_folder_obj,subfolder_name,number):
        subfolder_name="".join("" if c in "\/:*?\"<>|!." else c for c in  subfolder_name )
        subfolder=Path(f'{str(number).zfill(3)}-{subfolder_name}')
        fully_subfolder=Path(main_folder_obj/subfolder)
        Path.mkdir(fully_subfolder,parents=True,exist_ok=True)
        return  fully_subfolder

    def __save_article_html(self,title,html_data,subfolder_name):
        content=f"""<!DOCTYPE html>
        <html lang="tr">
        <head>
        <title>{title}</title>
        </head>
        <body><div style="width:800px; margin:0 auto;">
            {html_data}
            </div>
        </body>
        </html>"""
        file_name="".join("" if c in "\/:*?\"<>|!" else c for c in  title )
        file_name+=".html"
        folder_and_file_name=Path(subfolder_name/file_name)
        if not folder_and_file_name.exists():
            with open(folder_and_file_name,'w') as f:
                f.write(content)
                f.close()
        else:
            print(folder_and_file_name," file exists / dosya mevcut")

    def __save_supplementary_assets(self,file_name,url,folder_name):
        title = "".join("" if c in "\/:*?\"<>|!" else c for c in file_name)
        filename = Path(folder_name / title)
        resp = self.session.get(url)
        if resp.status_code==200:
            if not filename.exists():
                print(filename)
                with open(filename, 'wb') as f:
                    f.write(resp.content)
                    f.close()
            else:
                print(filename, " file exists / dosya mevcut")
        else:
            print('cant get file / dosya alınamadı')

    def __save_subtitles(self,file_name,url,folder_name):
        title = "".join("" if c in "\/:*?\"<>|!" else c for c in file_name)
        filename = Path(folder_name / title)
        resp = self.session.get(url)
        if resp.status_code==200:
            if not filename.exists():
                print(filename)
                with open(filename, 'wb') as f:
                    f.write(resp.content)
                    f.close()
            else:
                print(filename, " file exists / dosya mevcut")
        else:
            print('cant get file / dosya alınamadı')


    def __save_video_file(self,title,url,folder_name):
        title = "".join("" if c in "\/:*?\"<>|!" else c for c in title)
        filename = Path(folder_name / title)
        resp=self.session.get(url,stream=True)
        if resp.status_code==200:
            if not filename.exists():
                print(filename)
                with open(filename, 'wb') as f:
                    total_length = int(resp.headers.get('content-length'))
                    for chunk in progress.bar(resp.iter_content(chunk_size=1024), expected_size=(total_length / 1024) + 1):
                        if chunk:
                            f.write(chunk)
                            f.flush()
            else:
                print(filename, " file exists / dosya mevcut")
        else:
            print('cant get video infos / video bilgileri alınamadı')
   
    def download_course(self,choose):
        self.course_id,self.course_title=self.__get_course_title_and_id(choose)
        self.main_folder_obj=self.__main_folder_creator(self.course_title)
        self.course_chapter_and_lecture_status,self.course_chapter_and_lecture_json_data=self.__get_course_chapter_and_lecture(self.course_id)
        if self.course_chapter_and_lecture_status.status_code==200:
            subfolder_path=""
            i=1
            sub=1
            # print(self.course_chapter_and_lecture_json_data)
            for item in self.course_chapter_and_lecture_json_data:
                if item['_class'].lower()=='chapter':
                    subfolder_path=self.__sub_folder_creator(self.main_folder_obj,item['title'],sub)
                    sub+=1
                    continue
                elif item['_class'].lower() == 'lecture':
                    if item['asset']['asset_type'].lower()=='article':
                        url = f'''https://www.udemy.com/api-2.0/users/me/subscribed-courses/{str(self.course_id)}/lectures/{item['id']}?fields[lecture]=asset,supplementary_assets&fields[asset]=stream_urls,download_urls,captions,title,filename,data,body,media_sources,media_license_token'''
                        response=self.session.get(url,headers=self.header)
                        response_json=response.json()
                        # print(response_json)
                        if response.status_code==200:
                            file_name=item['title']
                            html_data=response_json['asset']['body']
                            self.__save_article_html(file_name,html_data,subfolder_path)
                            supplementary_assets=response_json['supplementary_assets']
                            if len(supplementary_assets)!=0:
                                for supp in supplementary_assets:
                                    if supp['download_urls'] == None:
                                        continue
                                    else:
                                        supp_file_name=supp['filename']
                                        supp_url= supp['download_urls']['File'][0]['file']
                                        self.__save_supplementary_assets(supp_file_name,supp_url,subfolder_path)
                            else:
                                print('no supplementary file / ek dosya yok')
                    elif item['asset']['asset_type'].lower()=='video':
                        url = f'''https://www.udemy.com/api-2.0/users/me/subscribed-courses/{str(self.course_id)}/lectures/{item['id']}?fields[lecture]=asset,supplementary_assets&fields[asset]=stream_urls,download_urls,captions,title,filename,data,body,media_sources,media_license_token'''
                        response=self.session.get(url,headers=self.header)
                        if response.status_code==200:
                            response_json = response.json()
                            video_url=response_json['asset']['media_sources'][0]['src']
                            video_file_name=str(i).zfill(3)+'-'+item['title_cleaned']+'.mp4'
                            self.__save_video_file(video_file_name,video_url,subfolder_path)
                            #save_subtitles
                            captions=video_url=response_json['asset']['captions']
                            if len(captions)!=0:
                                sub_file_name=video_file_name+'.srt'
                                sub_url=captions[0]['url']
                                self.__save_subtitles(sub_file_name,sub_url,subfolder_path)
                            else:
                                print('no subtitles / altyazı yok')

                            #
                            supplementary_assets=response_json['supplementary_assets']
                            if len(supplementary_assets)!=0:
                                for supp in supplementary_assets:
                                    if supp['download_urls'] == None:
                                        continue
                                    else:
                                        supp_file_name=supp['filename']
                                        supp_url= supp['download_urls']['File'][0]['file']
                                        self.__save_supplementary_assets(supp_file_name,supp_url,subfolder_path)
                            else:
                                print('no supplementary file / ek dosya yok')
                        i+=1
                elif item['_class'].lower() == 'quiz':
                    print('this is Quiz, passing...','Quiz bölümü. atlanıyor ...')
                    continue
                else:
                    print("i didnt see this class please contact me https://twitter.com/murderuo")
                    print("Bu bölümle karşılaşmadım, lütfen benimle irtibata geçin: https://twitter.com/murderuo")
                    continue

if __name__== '__main__':

    downloader=Udemy_Downloader()
    downloader.set_accesstoken()
    # downloader.create_session()
    downloader.list_my_course()
    secim=int(input('select the course to download / indirilecek kursu seciniz: '))
    downloader.download_course(secim)
    # downloader.do_you_wanna_subb()


