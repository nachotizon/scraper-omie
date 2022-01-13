# run.py
# 1.0.0
# 2022-01-12
# Nacho Tizon
# Web Scraper to download day-ahead market hourly prices in Spain from OMIE Market Operator web site https://www.omie.es/

import argparse
import requests
import certifi
import re
import sys
from datetime import datetime,timedelta




parser = argparse.ArgumentParser(description="Download day-ahead market hourly prices in Spain - OMIE Market Operator",epilog="by Nacho Tizon")
parser.add_argument("-d", dest='download', metavar=('Date From dd/mm/yyyy','Date To dd/mm/yyyy (Optional)') ,help="Download data for a specific day or a date range", nargs='+' )
args = parser.parse_args()

if args.download:
    if len(args.download)==1:
        args.download.append(args.download[0])
    try:
        dateFromD = datetime.strptime(args.download[0], '%d/%m/%Y').date()
        dateToD = datetime.strptime(args.download[1], '%d/%m/%Y').date()
        if dateFromD > dateToD:
            change = dateToD
            dateToD=dateFromD
            dateFromD=change
        delta = dateToD-dateFromD

    except ValueError:
        print("ERROR parsing parameters: "+args.download[0]+" "+args.download[1])
        sys.exit()
       
    fileOutput="marginalpdbc_"+args.download[0].replace("/","")+"_"+args.download[1].replace("/","")+".csv"

    
    by=b''
    print("Downloading day-ahead market hourly prices in Spain from "+args.download[0]+" to "+args.download[1])
    for dia in range (delta.days+1):
        dateFile=dateFromD + timedelta(days=dia)
        dateFile=dateFile.strftime('%Y%m%d')
        url ="https://www.omie.es/es/file-download?parents%5B0%5D=marginalpdbc&filename=marginalpdbc_"+dateFile+".1"
        session_requests = requests.session()

        result = session_requests.get(url, verify=certifi.where())

        if(result.status_code == 200):

            #Descargamos el archivo resultante 
            if result.headers.get('Content-Disposition') is not None:
                archivo=""
                filename = re.findall('filename=(.+)', result.headers.get('Content-Disposition'))
                archivo=filename[0]
                archivo=archivo.replace("\"","")
                byTemp=result.content
                byTemp=byTemp.replace(b'MARGINALPDBC;\r\n',b'')
                byTemp=byTemp.replace(b'*\r\n',b'')
                by=by+byTemp
    
            else:
                print("ERROR File not found, website: "+url)
        else:
            print("ERROR "+str(result.status_code)+" , website: "+url)

    if by !=b'':    
        file = open(fileOutput, "wb")            
        file.write(by)
        file.close()
        print("Downloaded. File "+fileOutput+" created!")

if not any(vars(args).values()):
   parser.print_help()