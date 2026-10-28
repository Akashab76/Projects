from bs4 import BeautifulSoup
import requests
import smtplib
import lxml
import os
from dotenv import load_dotenv

# Click on this link for the headers:
# https://httpbin.org/headers

url="https://www.amazon.in/dp/B0CHRY72DD/?_encoding=UTF8&pd_rd_i=B0CHRY72DD&ref_=sbx_be_s_sparkle_ssd_tt&qid=1743685021&pd_rd_w=4ttD2&content-id=amzn1.sym.df9fe057-524b-4172-ac34-9a1b3c4e647d%3Aamzn1.sym.df9fe057-524b-4172-ac34-9a1b3c4e647d&pf_rd_p=df9fe057-524b-4172-ac34-9a1b3c4e647d&pf_rd_r=V8QNQ687XFWT9SN5J9JG&pd_rd_wg=k6vuT&pd_rd_r=4bb733a6-d13c-4270-a07a-f6c5cc6cf78b&pd_rd_plhdr=t"
headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
"Accept-Language": "en-US,en;q=0.9"}

response=requests.get(url=url,headers=headers)
c=response.text
soup=BeautifulSoup(markup=c,parser="html.parser",features='lxml')
# print(soup.prettify())

p=soup.find(name="span",class_="a-price-whole")

text_p=p.getText()
text_list=[i for i in text_p if i.isnumeric()]
text_p="".join(text_list)
price=float(text_p)
print(price)
product_name=soup.find(name="span",id="productTitle").get_text().strip()
print(product_name)


# Sending mail:

# load_dotenv()
# email=os.environ["email"]
# password=os.environ["password"]


# if price<4000:
#     with smtplib.SMTP("smtp.gmail.com") as connect:
#         connect.starttls()
#         connect.login(user=email,password=password)
#         connect.sendmail(from_addr=email,to_addrs=email,msg=f"Subject:Low Price Alert \n\n {product_name} is available for ${price}.\n Click on {url} to buy".encode("utf-8"))

# Sending mail

load_dotenv()

email = os.getenv("email")
password = os.getenv("password")

if not email or not password:
    raise ValueError("Email or password missing from .env file")

if price < 4000:
    print("Price is below target. Sending email...")

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as connect:
            connect.ehlo()
            connect.starttls()
            connect.ehlo()

            connect.login(user=email, password=password)

            message = (
                f"Subject: Low Price Alert\n\n"
                f"{product_name} is available for Rs. {price}.\n"
                f"Click here to buy: {url}"
            )

            connect.sendmail(
                from_addr=email,
                to_addrs=email,
                msg=message
            )

        print("Email sent successfully!")

    except Exception as e:
        print(f"Email sending failed: {type(e).__name__}: {e}")

else:
    print(f"Price Rs. {price} is not below Rs. 4000.")
