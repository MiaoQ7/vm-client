from .isms import ISMS
from app.libs import ihttp
import time
import re
from loguru import logger

areaCodeToCountry = {
    "AB": "116",  # Abkhazia
    "AF": "114",  # Afghanistan Afghanistan
    "AL": "160",  # Albania Albania
    "DZ": "8",  # Algeria Algeria
    "AS": "161",  # American Samoa American Samoa
    "AO": "11",  # Angola Angola
    "AI": "234",  # Anguilla Anguilla
    "AG": "137",  # Antigua and Barbuda Antigua and Barbuda
    "AR": "32",  # Argentinas Argentinas
    "AM": "115",  # Armenia Armenia
    "AW": "225",  # Aruba Aruba
    "AU": "270",  # Australia Australia
    "AT": "268",  # Austria Austria
    "AZ": "61",  # Azerbaijan Azerbaijan
    "BS": "151",  # Bahamas Bahamas
    "BH": "124",  # Bahrain Bahrain
    "BD": "4",  # Bangladesh Bangladesh
    "BB": "110",  # Barbados Barbados
    "BY": "56",  # Belarus Belarus
    "BE": "76",  # Belgium Belgium
    "BZ": "261",  # Belize Belize
    "BJ": "72",  # Benin Benin
    "BM": "345",  # Bermuda Bermuda
    "BT": "92",  # Bhutan Bhutan
    "BO": "152",  # Bolivia Bolivia
    "BA": "108",  # Bosnia and Herzegovina Bosnia and Herzegovina
    "BW": "26",  # Botswana Botswana
    "BR": "14",  # Brazil Brazil
    "BN": "156",  # Brunei Darussalam Brunei Darussalam
    "BG": "57",  # Bulgaria Bulgaria
    "BF": "74",  # Burkina Faso Burkina Faso
    "BI": "93",  # Burundi Burundi
    "KH": "99",  # Cambodia Cambodia
    "CM": "53",  # Cameroon Cameroon
    "CA": "143",  # Canada Canada
    "CV": "240",  # Cape Verde Cape Verde
    "KY": "157",  # Cayman islands Cayman islands
    "CF": "167",  # Central African Republic Central African Republic
    "TD": "118",  # Chad Chad
    "CL": "148",  # Chile Chile
    "CN": "103",  # China China
    "CO": "48",  # Colombia Colombia
    "KM": "226",  # Comoros Comoros
    "CG": "80",  # Congo Congo
    "CD": "24",  # Congo (Dem. Republic) Congo (Dem. Republic)
    "CR": "73",  # Costa Rica Costa Rica
    "CI": "55",  # Cote d'Ivoire/Ivory Coast Cote d'Ivoire/Ivory Coast
    "HR": "239",  # Croatia Croatia
    "CU": "146",  # Cuba Cuba
    "CW": "237",  # Curacao Curacao
    "CY": "130",  # Cyprus Cyprus
    "CZ": "125",  # Czech Republic Czech Republic
    "DK": "267",  # Denmark Denmark
    "DJ": "138",  # Djibouti Djibouti
    "DM": "272",  # Dominica Dominica
    "DO": "112",  # Dominican Republic Dominican Republic
    "EC": "37",  # Ecuador Ecuador
    "EG": "13",  # Egypt Egypt
    "SV": "38",  # El Salvador El Salvador
    "GQ": "96",  # Equatorial Guinea Equatorial Guinea
    "ER": "304",  # Eritrea Eritrea
    "EE": "123",  # Estonia Estonia
    "ET": "9",  # Ethiopia Ethiopia
    "FO": "262",  # Faroe Islands Faroe Islands
    "FJ": "236",  # Fiji Fiji
    "FI": "139",  # Finland Finland
    "FR": "25",  # France France
    "GF": "140",  # French Guiana French Guiana
    "GA": "64",  # Gabon Gabon
    "GM": "113",  # Gambia Gambia
    "GE": "149",  # Georgia
    "DE": "85",  # Germany Germany
    "GH": "42",  # Ghana Ghana
    "GR": "147",  # Greece Greece
    "GL": "351",  # Greenland Greenland
    "GD": "153",  # Grenada Grenada
    "GP": "126",  # Guadeloupe Guadeloupe
    "GT": "133",  # Guatemala Guatemala
    "GN": "170",  # Guinea Guinea
    "GW": "105",  # Guinea-Bissau Guinea-Bissau
    "GY": "117",  # Guyana Guyana
    "HT": "15",  # Haiti Haiti
    "HN": "31",  # Honduras Honduras
    "HK": "163",  # Hong Kong Hong Kong
    "HU": "91",  # Hungary Hungary
    "IS": "303",  # Iceland Iceland
    "IN": "2",  # India India
    "ID": "135",  # Indonesia Indonesia
    "IR": "16",  # Iran Iran
    "IQ": "83",  # Iraq Iraq
    "IE": "121",  # Ireland Ireland
    "IL": "54",  # Israel Israel
    "IT": "128",  # Italy Italy
    "JM": "45",  # Jamaica Jamaica
    "JP": "169",  # Japan Japan
    "JO": "52",  # Jordan Jordan
    "KZ": "47",  # Kazakhstan Kazakhstan
    "KE": "43",  # Kenya Kenya
    "KR": "273",  # Korea Korea
    "XK": "347",  # Kosovo Kosovo
    "KW": "104",  # Kuwait Kuwait
    "KG": "51",  # Kyrgyzstan Kyrgyzstan
    "LA": "86",  # Lao People's Lao People's
    "LV": "154",  # Latvia Latvia
    "LB": "266",  # Lebanon Lebanon
    "LS": "36",  # Lesotho Lesotho
    "LR": "168",  # Liberia Liberia
    "LY": "58",  # Libya Libya
    "LI": "348",  # Liechtenstein Liechtenstein
    "LT": "166",  # Lithuania Lithuania
    "LU": "131",  # Luxembourg Luxembourg
    "MO": "301",  # Macau Macau
    "MK": "242",  # Macedonia Macedonia
    "MG": "134",  # Madagascar Madagascar
    "MW": "41",  # Malawi Malawi
    "MY": "94",  # Malaysia Malaysia
    "MV": "106",  # Maldives Maldives
    "ML": "62",  # Mali Mali
    "MT": "229",  # Malta Malta
    "MQ": "111",  # Martinique Martinique
    "MR": "101",  # Mauritania Mauritania
    "MU": "59",  # Mauritius Mauritius
    "MX": "28",  # Mexico Mexico
    "MD": "68",  # Moldova, Republic of Moldova, Republic of
    "MC": "241",  # Monaco Monaco
    "MN": "265",  # Mongolia Mongolia
    "ME": "142",  # Montenegro Montenegro
    "MS": "271",  # Montserrat Montserrat
    "MA": "39",  # Morocco Morocco
    "MZ": "10",  # Mozambique Mozambique
    "MM": "33",  # Myanmar Myanmar
    "NA": "6",  # Namibia Namibia
    "NP": "20",  # Nepal Nepal
    "NL": "95",  # Netherlands Netherlands
    "NC": "263",  # New Caledonia New Caledonia
    "NZ": "264",  # New Zealand New Zealand
    "NI": "67",  # Nicaragua Nicaragua
    "NE": "89",  # Niger Niger
    "NG": "22",  # Nigeria Nigeria
    "NO": "127",  # Norway Norway
    "OM": "79",  # Oman
    "PK": "3",  # Pakistan Pakistan
    "PS": "238",  # Palestine Palestine
    "PA": "44",  # Panama Panama
    "PG": "7",  # Papua new gvineya Papua new gvineya
    "PY": "49",  # Paraguay Paraguay
    "PE": "17",  # Peru Peru
    "PH": "102",  # Philippines Philippines
    "PL": "87",  # Poland Poland
    "PT": "107",  # Portugal Portugal
    "PR": "120",  # Puerto Rico Puerto Rico
    "QA": "75",  # Qatar Qatar
    "RE": "78",  # Reunion Reunion
    "RO": "129",  # Romania Romania
    "RU": "27",  # Russian Federation Russian Federation
    "RW": "63",  # Rwanda Rwanda
    "KN": "164",  # Saint Kitts and Nevis Saint Kitts and Nevis
    "LC": "141",  # Saint Lucia Saint Lucia
    "VC": "158",  # Saint Vincent Saint Vincent
    "WS": "231",  # Samoa Samoa
    "ST": "235",  # Sao Tome and Principe Sao Tome and Principe
    "SA": "70",  # Saudi Arabia Saudi Arabia
    "SN": "84",  # Senegal Senegal
    "RS": "122",  # Serbia Serbia
    "SC": "269",  # Seychelles Seychelles
    "SL": "150",  # Sierra Leone Sierra Leone
    "SG": "232",  # Singapore Singapore
    "SX": "349",  # Sint Maarten Sint Maarten
    "SK": "233",  # Slovakia Slovakia
    "SI": "162",  # Slovenia Slovenia
    "SB": "228",  # Solomon Islands Solomon Islands
    "SO": "109",  # Somalia Somalia
    "ZA": "1",  # South Africa South Africa
    "SS": "100",  # South Sudan South Sudan
    "ES": "66",  # Spain Spain
    "LK": "30",  # Sri Lanka Sri Lanka
    "SD": "65",  # Sudan Sudan
    "SR": "132",  # Suriname Suriname
    "SZ": "23",  # Swaziland Swaziland
    "SE": "136",  # Sweden Sweden
    "CH": "119",  # Switzerland Switzerland
    "SY": "90",  # Syrian Arab Republic Syrian Arab Republic
    "TW": "165",  # Taiwan Taiwan
    "TJ": "155",  # Tajikistan Tajikistan
    "TZ": "29",  # Tanzania Tanzania
    "TH": "71",  # Thailand Thailand
    "TL": "35",  # Timor-Leste Timor-Leste
    "TG": "88",  # Togo Togo
    "TO": "227",  # Tonga Tonga
    "TT": "98",  # Trinidad and Tobago Trinidad and Tobago
    "TN": "34",  # Tunisia Tunisia
    "TR": "50",  # Turkey Turkey
    "TM": "60",  # Turkmenistan Turkmenistan
    "TC": "159",  # Turks and Caicos Island Turks and Caicos Island
    "UG": "40",  # Uganda Uganda
    "UA": "12",  # Ukraine Ukraine
    "AE": "97",  # United Arab Emirates United Arab Emirates
    "GB": "77",  # United Kingdom United Kingdom
    "US": "69",  # United States United States
    "UV": "346",  # United States virt United States virt
    "UY": "82",  # Uruguay Uruguay
    "UZ": "21",  # Uzbekistan Uzbekistan
    "VU": "350",  # Vanuatu Vanuatu
    "VE": "46",  # Venezuela Venezuela
    "VN": "18",  # Viet nam Viet nam
    "VG": "230",  # Virgin Islands Virgin Islands
    "YE": "81",  # Yemen Yemen
    "ZM": "5",  # Zambia Zambia
    "ZW": "19",  # Zimbabwe Zimbabwe
}

# API  https://sms-code.ru/cabinet/api
class SMSCodeClient(ISMS):

    def __init__(self, params, vpsID, serverPath):
        global areaCodeToCountry
        if params is None:
            params = {
                "area": {
                    "code": "7",
                    "name": "Russia",
                    "abbr": "RU"
                }
            }
        self.service = params.get("projectId", "14")
        self.data = params
        self.server_url = params.get("serverUrl", "https://sms-code.ru/api.php")
        abbr = self.data.get("area").get("abbr")
        self.country = areaCodeToCountry.get(abbr)
        if self.country is None:
            areaName = self.data.get("area").get("name")
            raise Exception(f"卡商没有配置对应的国家{areaName}")
        self.token = params.get("account", "MgzeJQGqh1azdg9hzKfkFwcc6o0Lw7dE")

        self.tzid = None
        self.cellNum = None
        self.hasYuE = False
        self.msg = None
        self.platformCode = params.get("platformCode", "sms-code")
        self.vpsID = vpsID
        self.serverPath = serverPath

    def send(self, action, params):
        params["api_key"] = self.token
        params['method'] = action
        res = self.loopSendGet(self.server_url, params)
        if res.ok:
            try:
                return res.json()
            except Exception:
                pass
        return None

    def isOk(self, data):
        return data and data['status'] == "ok"

    '''
    https://sms-code.ru/api.php?api_key=${api_key}&method=get_balance
     {"status":"ok","message":"","data":{"balance":"100.00"}}
    '''
    def login(self):
        params = {
        }
        data = self.send("get_balance", params)
        if self.isOk(data):
            self.hasYuE = float(data['data']['balance']) >= 8
        return self.hasYuE

    '''
    https://sms-code.ru/api.php?api_key=${api_key}&method=phone&service=14&country=2
    Responses:
Incorrect API KEY: {"status":"error","message":"No access","data":[]}
Invalid provider, service or country: {"status":"error","message":"Invalid provider, service or country","data":[]}
Invalid service: {"status":"error","message":"Invalid service","data":[]}
Insufficient funds: {"status":"error","message":"Insufficient funds","data":[]}
No numbers available: {"status":"error","message":"No numbers available","data":[]}
Failed to get the number: {"status":"error","message":"Failed to get the number, try one more time","data":[]}
Failed to get token (only for Provider 1): {"status":"error","message":"Failed to get token","data":[]}
Phone number received successfully: {"status":"ok","message":"","data":{"activation":44100334,"number":"919380403998"}}
    '''
    def getCellNum(self):
        if self.cellNum is None:
            params = {
                "country": self.country,
                "service": self.service
            }
            for i in range(10):
                data = self.send("phone", params)
                if self.isOk(data):
                    self.tzid = data['data']['activation']
                    self.cellNum = data['data']['number']
                    errormessage = self.checkPhone(self.cellNum, self.data["area"]["code"])
                    if errormessage is None:
                        break
                    else:
                        self.phoneRelease(8)

                time.sleep(3)

            if self.cellNum is None:
                return None
            else:
                self.logPhone(self.cellNum)

        if self.cellNum is not None and self.data is not None and self.data.get("area") is not None and self.data.get("area").get("code") is not None:
            code = self.data.get("area").get("code")  # 去掉号码中的区号
            matches = re.match(code, self.cellNum)
            if matches is None:
                # return self.cellNum[len(code): len(self.cellNum)]
                return "+" + code + self.cellNum
        return "+" + self.cellNum

    '''
    https://sms-code.ru/api.php?api_key=${api_key}&method=sms&activation=123
    Responses:
Wrong phone number: {"status":"error","message":"Wrong phone number","data":[]}
SMS code has not been received yet: {"status":"error","message":"SMS code has not been received yet, please try one more time","data":[]}
Failed to receive SMS, get another phone number: {"status":"error","message":"Failed to receive SMS, get another phone number","data":[]}
Sms code received successfully: {"status":"ok","message":"","data":"123-456"}
    '''
    def querySMS(self):
        # if self.msg is not None:
        self.msg = None
        params = {
            "activation": self.tzid
        }
        timeout = int(round(time.time() * 1000)) + 1000 * 60 * 3
        for i in range(45):
            if int(round(time.time() * 1000)) > timeout:
                break
            data = self.send("sms", params)
            if self.isOk(data):
                self.msg = self.parseDYSMSCode(data['data'])
                return self.msg
            time.sleep(5)
        return self.msg

    '''
    https://sms-code.ru/api.php?api_key=${api_key}&method=cancel&activation=123
    Responses:
Wrong phone number: {"status":"error","message":"Wrong phone number":[]}
The phone number is already canceled: {"status":"error","The phone number is already canceled","data":[]}
Failed cancel: {"status":"error","message":"Failed cancel":[]}
Number canceled successfully: {"status":"ok","message":"",""}
    '''
    def phoneRelease(self, status):
        params = {
            "activation": self.tzid,
        }
        result = self.send("cancel", params)
        self.cellNum = None

    def add2BlackList(self, status, msg):
        if self.cellNum is not None:
            self.logPhone(self.cellNum)
            self.addHistoryPhone(self.cellNum, self.data.get("area"), status, self.platformCode, self.msg, None, msg)
        if self.cellNum is not None and status == "success":
            self.phoneRelease(6)
        elif status == "failed":
            self.phoneRelease(8)
        else:
            self.phoneRelease(8)
        self.cellNum = None
