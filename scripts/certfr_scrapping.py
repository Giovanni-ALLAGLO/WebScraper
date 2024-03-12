import requests
import bs4
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from scrapping_interface import ScrapperInterface
from ..utils import encode, months_Fr2En

class CertfrScrapper(ScrapperInterface):
    """
    CertfrScrapper class for scraping data from the CERT-FR website.

    Methods
    -------
    __init__(header = None)
    Initialize CertfrScrapper object.

    parser( header = None)
        Main method to extract data from the CERT-FR website.
    """
     
    def __init__(self,header: dict = None) -> None:
        """
        Initialize an instance of CertfrScrapper object.

        Parameters
        ----------
        header : dict
            Optional HTTP headers for the requests (default value : None).
        """
        
        self.data_collect_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.data: list[pd.DataFrame] = CertfrScrapper.parser() if header==None else CertfrScrapper.parser(header) 
        pass
    

    @classmethod
    def parser(cls,header: dict = None) -> list[pd.DataFrame]:
        """
        Method to parse and extract data from the CERT-FR website.

        Parameters
        ----------
        head : dict
            HTTP headers for the requests (default value is None)

        Returns
        -------
        list
            List of dataframe containing extracted data.
        """
        rubrique_list: list[pd.DataFrame] = []
        try:
            response = requests.get(cls.URL,headers= header)
            response.raise_for_status() #leve une exception si le status de la requete différent de 200

            soup = BeautifulSoup(response.text, "html.parser")
            div_container = soup.find_all("div", {"class": "row"})
            if div_container:
                info = []
                for i , element in enumerate(div_container):
                    #
                    div_cards = element.find("div", {"class": "cards"})
                    info.append({"general_title": encode(div_cards.find("h2").text.strip()), "general_description":encode(div_cards.find("h3").text.strip()) })
                    #
                    rubrique_list.append(lecture_donnee_cert(element,i))
                info_dataframe = pd.DataFrame(info)
            else:
                print("failed: Container <div>...</div> is Empty")
                return None
            
        except requests.exceptions.HTTPError as http_err:
            print(http_err)
            return None
        except Exception as e:
            print(f"Error: {e}")
            return None
        
        rubrique_list.append(info_dataframe)
        
        return rubrique_list
    


def lecture_donnee_cert(element: bs4.element.Tag ,index: int) -> pd.DataFrame:
    """Extracts data from the different sections of the CERT-FR site from the index provided."""
    if index == 0: # Data of security alert
        return lecture_alerte(element)
    
    elif index > 0 and index<5: # Data of threats and incidents,safety notice,indicators of compromise,hardening and recommandations,
        return lecture_autres_rubriques(element)

    elif index == 5: # Data of News
        return lecture_actualite(element)
    else:
        print("Alert: Modification du site - nouvelle rubrique disponible")
        return None


def lecture_alerte(el):
    """Extract infromation about the "alert secutity" section from the HTML tag."""
    data = pd.DataFrame()
    
    div_item = el.find("div", {"class": "items-list"})
    item_title = div_item.find_all("span" , {"class":"item-title"})

    data["alerte_id"] = [tag.text.strip() for tag in div_item.find_all("span" , {"class":"item-ref"})]
    
    data["title"] = [encode(item.find('a').text.strip()) for item in item_title]
    
    data["status"] = [encode(tag.text.strip()) for tag in div_item.find_all("span", {"class": "item-status"})]

    data["link"]= [normalise_url(item.find('a', href=True)['href']) for item in item_title]

    data["publication_date"] = [normalise_date(date.text.strip()) for date in div_item.find_all("span" , {"class":"item-date"})]

    data["source"] =[CertfrScrapper.SOURCE for i in item_title ]
    
    return data



def lecture_autres_rubriques(el):
    """Extract information on other subjects from the HTML tag."""
    data = pd.DataFrame()
    
    div_item = el.find("div", {"class": "items-list"})
    item_title = div_item.find_all("span" , {"class":"item-title"})

    data["rubrique_id"] = [tag.text.strip() for tag in div_item.find_all("span" , {"class":"item-ref"})]
    
    data["title"] = [encode(item.find('a').text.strip()) for item in item_title]
    
    data["link"]= [normalise_url(item.find('a', href=True)['href']) for item in item_title]

    data["publication_date"] = [normalise_date(date.text.strip()) for date in div_item.find_all("span" , {"class":"item-date"})]

    data["source"] =[CertfrScrapper.SOURCE for i in item_title ]
    
    return data
        

def lecture_actualite(el):
    """Extract information about the "news" section of the HTML tag."""
    data = pd.DataFrame()
    
    section_item = el.find("section", {"class": "items-expanded"})
    item_title = section_item.find_all("div" , {"class":"item-title"})

    data["news_id"] = [tag.text.strip() for tag in section_item.find_all("span" , {"class":"item-ref"})]

    data["title"] = [encode(item.find('a').text.strip()) for item in item_title]
    
    data["description"] = [encode(tag.text.strip()) for tag in section_item.find_all("section", {"class": "item-excerpt"})]
   
    data["link"]= [normalise_url(item.find('a', href=True)['href']) for item in item_title]
    
    data["publication_date"] = [normalise_date(date.text.strip().split("le ")[1]) for date in section_item.find_all("span" , {"class":"item-date"})]
    
    data["source"] =[CertfrScrapper.SOURCE for i in item_title ]
    return data


def normalise_url(path_url: str) -> str:
    """Normalizes the URL by appending the base prefix."""
    return CertfrScrapper.URL + path_url

def normalise_date(date: str) -> str:
    """Normalized date in the format YYYY-MM-DD HH:MM:SS."""
    try:
        date = encode(date)
        mois = date.split()[1]
        date = datetime.strptime(date.replace(mois,months_Fr2En(mois)), "%d %B %Y")
        # Formater la date selon le format standart
        return date.strftime("%Y-%m-%d")
    except ValueError as val_err:
        try:
            date = datetime.strptime(date, "%B %d, %Y")
            return date.strftime("%Y-%m-%d")
        except (ValueError) as val_err:
            print("Error in normalise date (format):",val_err)
    except Exception as err:
        print("Error occured in normalise_date", err)
    return "! "+ date



if __name__ == "__main__":
    url = "https://www.cert.ssi.gouv.fr"
    CertfrScrapper.URL = url
    CertfrScrapper.SOURCE = "fr"
    print(CertfrScrapper.parser())