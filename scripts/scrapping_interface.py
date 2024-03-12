class ScrapperInterface:
    """
    A class to scrape vulnerability data from the NVD (National Vulnerability Database).

    ...

    Attributes
    ----------
    URL : str
        Base URL for the website.
    SOURCE : str
        Name of data source

    Methods
    -------

    parser(head=None)
        Extracts data from target website.
    
    """

    URL: str = None
    SOURCE: str = None

    @classmethod
    def parser(cls,header=None):
        return 0

