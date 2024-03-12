
import requests
import re
import bs4
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from scrapping_interface import ScrapperInterface

class NvdScrapper(ScrapperInterface):
    """
    A class to scrape vulnerability data from the NVD (National Vulnerability Database).

    ...

    Methods
    -------
    __init__(header=None)
        Initializes an instance of the scraper class.
    parser(head=None)
        Exctract vulnerability data from the NVD website and returns a Pandas DataFrame.
    """
    def __init__(self,header: dict = None) -> None:
        """
        Constructs all the necessary attributes for the NvdScrapper object.

        Parameters
        ----------
        header : dict, optional
            HTTP header for the request (default is None).
        """

        self.data_collect_time: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.data: pd.DataFrame = NvdScrapper.parser() if header==None else NvdScrapper.parser(header)
        pass
    
    @classmethod
    def parser(cls,header: dict = None) -> pd.DataFrame:
        """
        Parses and Extract vulnerability data from the NVD website and returns a Pandas DataFrame.

        Parameters
        ----------
        head : Optional[Dict[str, str]], optional
            HTTP header for the request (default is None).

        Returns
        -------
        pd.DataFrame
            DataFrame containing vulnerability data.
        """
        rows_list : list[dict] = []
        try:
            response = requests.get(cls.URL,headers= header)
            response.raise_for_status() #leve une exception si le status de la requete différent de 200

            soup = BeautifulSoup(response.text, "html.parser")
            ul_container = soup.find("ul", {"id": "latestVulns"})
            if ul_container:
                li_container = ul_container.find_all("li")
                for element in li_container:
                    rows_list.append(lecture_donnee_cve(element))
            else:
                print("failed: Container <ul>...</ul> is Empty")
            
        except requests.exceptions.HTTPError as http_err:
            print(http_err)
            return None
        except Exception as e:
            print(f"Error occured: {e}")
            return None
        
        return pd.DataFrame(rows_list)
    


def lecture_donnee_cve(li_element: bs4.element.Tag) -> dict:
    """
    Extracts details of a vulnerability.

    Parameters
    ----------
    li_element : bs4.element.Tag
        The li element containing information about the vulnerability.

    Returns
    -------
    dict
        Dictionary containing details of the vulnerability.
    """
    try:
        # Details sur la vulnérabilité
        vulnerabilite = li_element.find("div",{"class": "col-lg-9"})
        #identifiant du cve
        cve_id = vulnerabilite.find('strong').text.strip()
        # petite description du cve
        cve_description = vulnerabilite.find('strong').next_sibling.strip()
        
        #lien à consulter pour plus de detail
        cve_lien = vulnerabilite.find('a', href=True)['href']
        cve_lien = normalise_url(cve_lien)
        
        #date de publication
        cve_date_publication = vulnerabilite.find('strong', string='Published:').next_sibling.strip()
        cve_date_publication = normalise_date(cve_date_publication)
                    

        # Score et sévérité de la vunérabilité
        criticite = li_element.find("div",{"class": "col-lg-3"})

        version_cvss = criticite.find("em").text.strip()
        version_cvss = normalise_version(version_cvss)

        score_cvss = criticite.find("a").text.strip()
        score_cvss = normalise_score(score_cvss)
        return {"cve_id":cve_id, "cve_description":cve_description, "cve_lien":cve_lien , "cve_date_publication":cve_date_publication, "version_cvss":version_cvss, "score_cvss":score_cvss, "source":NvdScrapper.SOURCE}
    
    except Exception as e:
        print("Error in lecture_donne_cve", e)
        return None


#Fonctions de normalisation de valeurs
def normalise_url(path_url: str) -> str:
    """Normalizes the URL by appending the base prefix."""
    return NvdScrapper.URL + path_url

def normalise_date(date_publication: str) -> str:
    """Normalized date in the format YYYY-MM-DD HH:MM:SS."""
    try:
        pattern = re.compile(r"(.*?) -\d+")
        date_str = re.findall(pattern,date_publication)
        # Convertir la chaîne en objet datetime
        date = datetime.strptime(date_str[0], "%B %d, %Y; %I:%M:%S %p")
        # Formater la date selon le format standart
        return date.strftime("%Y-%m-%d %H:%M:%S")
    except re.error as re_err:
        print("Error in normalise_date (regex)",re_err)
        return "! "+ date_publication
    except ValueError as val_err:
        print("Error in normalise_date (format)", val_err)
        return "! "+ date_str

def normalise_score(score: str) ->str:
    """Return a CVSS score between 0 and 10."""
    try:
        pattern = re.compile(r"\d+\.\d+")
        return re.findall(pattern,score)[0]
    except re.error as re_err:
        print(f"Error in normalise_score (regex): {re_err}")
        return "! "+score
    except IndexError as index_err:
        print(f"Error in normalise_score (index): {index_err}")
        return "! "+score
    

def normalise_version(version: str) -> str:
    """Return a version of CVSS metrics"""
    if version[-1]==":":
        return version[:-1]
    return version




if __name__ == "__main__":
    url = "https://nvd.nist.gov"
    NvdScrapper.URL = url
    print(NvdScrapper.parser())