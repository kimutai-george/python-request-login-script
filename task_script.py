import requests
from bs4 import BeautifulSoup, element
import time
import sys

# Initial Amazon login page
init_url = 'https://www.amazon.co.uk/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.co.uk%2F%3Fref_%3Dnav_ya_signin&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=gbflex&openid.mode=checkid_setup&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0'

# Setting user-agent header to our HTTP request and indicates request client 
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}


# Capture solving functionality
def validate_capture(session, captcha_image_url):
    CAP_API_KEY = 'YOUR_CAPSOLVER_API' # Capsolver API
    captcha_image_data = session.get(captcha_image_url).content

    url = "https://api.capmonster.cloud/in.php"
    files = {'file': captcha_image_data}
    data = {
        'key': CAP_API_KEY,
        'method': 'post',
    }
    response = requests.post(url, data=data, files=files)
    try:
        res = response.json()
        print(res)
        if "error" in response and res["error"] == "ERROR_KEY_DOES_NOT_EXIST":
            print("The API key does not exist. Please check or regenerate.")
            return None
    except requests.exceptions.JSONDecodeError:
        print("Failed to decode JSON from response")
        return None
        return None

    if response["status"] == 1:
        captcha_id = response["request"]
        for _ in range(30):
            solution = requests.get(
                f"https://api.capmonster.cloud/res.php?key={CAP_API_KEY}&action=get&id={captcha_id}").json()
            if solution["status"] == 1:
                return solution["request"]
            time.sleep(5)
        return None
    else:
        print(f"Error: {response['request']}")
        return None


# Create a session object to persist parameters,headers and cookies across the requests
with requests.Session() as session:
    # Update  our session object with headers
    session.headers.update(headers)

    # We do two fetch. initial fetch and 2nd fetch to get cookies
    init_res_1 = session.get(init_url)
    init_res_2 = session.get(init_url)

    # Get cookies from our request
    cookies = init_res_2.cookies
    our_cookie = {}
    for cookie in cookies:
        our_cookie[cookie.name] = cookie.value


    # using BeautifulSoup to parse our html content and find specific elements using their unique tag names
    our_content = BeautifulSoup(init_res_2.text, 'html.parser')

    # Get form action url from login form
    form_action = our_content.find('form', {'name': 'signIn'}).get('action')


    # create a dict named init_data constructed from our login form data
    init_data = {
        'appActionToken': our_content.find('input', {'name': 'appActionToken'}).get('value'),
        'appAction': our_content.find('input', {'name': 'appAction'}).get('value'),
        'subPageType': our_content.find('input', {'name': 'subPageType'}).get('value'),
        'openid': our_content.find('input', {'name': 'openid.return_to'}).get('value'),
        'prevRID': our_content.find('input', {'name': 'prevRID'}).get('value'),
        'workflowState': our_content.find('input', {'name': 'workflowState'}).get('value'),
        'email': 'AMAZON_CO_UK_EMAIL',
        'password': 'AMAZON_CO_UK_PASSWORD',
        'create': our_content.find('input', {'name': 'create'}).get('value'),
        "metadata1": "true",
        "aaToken": "259-6866135-8417424-1696451000747"
    }

    session.get(form_action)

    # Sending post request to our form action with data loaded from login form
    init_res_3 = session.post(form_action, data=init_data, cookies=our_cookie)

    # after post request
    # Check if the the results contains captcha functionality
    if "captcha" in init_res_3.text:
        # using BeautifulSoup to parse our html content and find specific elements using their unique tag names
        our_captcha_content = BeautifulSoup(init_res_3.text, 'html.parser')
        
        # Extract image from our html content
        capture_image = our_captcha_content.find('img', alt='captcha')

        # Exctract source url for our captcha image
        if capture_image and isinstance(capture_image, element.Tag):
            capture_image_url = capture_image['src']
        else:
            print("Image captcha not found")
            sys.exit(1)

        # Get form action url from captcha form
        form_action_on_capture = our_captcha_content.find('form', {'name': 'signIn'}).get('action')

        # Run captcha validation and solving
        validate_captcha = validate_capture(session, capture_image_url)

        if validate_captcha:

            # If capture solving is successfull, construct a dict with form data from our captcha form
            current_data = {
                "cvf_captcha_captcha_token": our_captcha_content.find('input',
                                                                      {'name': 'cvf_captcha_captcha_token'}).get(
                    'value'),
                "cvf_captcha_captcha_type": our_captcha_content.find('input', {'name': 'cvf_captcha_captcha_type'}).get(
                    'value'),
                "cvf_captcha_js_enabled_metric": "0",
                "clientContext": our_captcha_content.find('input', {'name': 'clientContext'}).get('value'),
                "openid.pape.max_auth_age": our_captcha_content.find('input', {'name': 'openid.pape.max_auth_age'}).get(
                    'value'),
                "openid.identity": our_captcha_content.find('input', {'name': 'openid.identity'}).get('value'),
                "openid.assoc_handle": our_captcha_content.find('input', {'name': 'openid.assoc_handle'}).get('value'),
                "openid.mode": our_captcha_content.find('input', {'name': 'openid.mode'}).get('value'),
                "openid.claimed_id": our_captcha_content.find('input', {'name': 'openid.claimed_id'}).get('value'),
                "pageId": our_captcha_content.find('input', {'name': 'pageId'}).get('value'),
                "openid.ns": our_captcha_content.find('input', {'name': 'openid.ns'}).get('value'),
                "verifyToken": our_captcha_content.find('input', {'name': 'verifyToken'}).get('value'),
                "cvf_captcha_input": validate_captcha
            }

            # Sending post request to our form action with data loaded from captcha form and get login results
            final_login = session.post(form_action, data=current_data, cookies=our_cookie)
            print(final_login)  # Login Successfull

    # if No captcha, return login results
    print(init_res_3)  # Login Successfull
