from bs4 import BeautifulSoup
import csv
from datetime import datetime

#Function to extract Date-Time in 24hr format
def datetimeextractor(date_time):
    dt = datetime.strptime(date_time, '%b %d, %Y, %I:%M:%S %p %Z')
    formatted_date = dt.strftime("%Y-%m-%d")
    formatted_time = dt.strftime("%H:%M:%S")
    return formatted_date, formatted_time

# Function to parse HTML and extract data
def extract_data_from_html(html_content):
    i=1
    soup = BeautifulSoup(html_content, 'lxml')
    records = []

    # Find all relevant divs
    divs = soup.find_all('div', class_='outer-cell mdl-cell mdl-cell--12-col mdl-shadow--2dp')
    
    for div in divs:
        i=i+1
        try:
            # Extracting details
            # service = div.find('p', class_='mdl-typography--title').get_text(strip=True)
            content_cells = div.find_all('div', class_='content-cell mdl-cell mdl-cell--6-col mdl-typography--body-1')
            if len(content_cells) < 1:
                raise ValueError("Missing content cells")
            content = content_cells[0]
            activity_part=content.contents[0].strip()
            datetime_part = content.contents[-1].strip()
            if('₹' not in activity_part):
                activity = 'Used'
            else:
                activity = activity_part.split('₹')[0].strip()
            if(activity=='Used'):
                amount=None
                recipient=None
                account=None
                status=None
                
            if(activity=='Paid'):
                amount = activity_part.split('₹')[1].split(' ')[0]
                if(('to' in activity_part.split('.')[1]) & ('using' in activity_part)):
                    recipient = activity_part.split('to ')[1].split(' using')[0]
                    account = activity_part.split('Account ')[1]
                elif(('to' in activity_part.split('.')[1]) & ('using' not in activity_part)):
                    recipient = activity_part.split('to ')[1]
                    account=None
                elif(('to' not in activity_part.split('.')[1]) & ('using' in activity_part)):
                    recipient=None
                    account = activity_part.split('Account ')[1]  
                else:
                    recipient=None
                    account=None
                    
            if(activity=='Received'):
                amount = activity_part.split('₹')[1][0:6]
                recipient=None
                account=None
                
            if(activity=='Sent'):
                amount = activity_part.split('₹')[1].split(' ')[0]
                recipient=None
                if('Account' in activity_part):
                    account = activity_part.split('Account ')[1]
                else:
                    account=None
                
            formatted_date,formatted_time = datetimeextractor(datetime_part)
            # Extract products and details
            if(activity!='Used'):
                product_details = div.find('div', class_='content-cell mdl-cell mdl-cell--12-col mdl-typography--caption')
                if not product_details:
                    raise ValueError("Missing product details cell")
                details = product_details.find_all('br')
                if len(details) < 3:
                    raise ValueError("Missing details in product details cell")
                status = details[3].next_sibling.strip()
            # Append extracted data as a tuple
            records.append((activity, amount, recipient, account, formatted_date,formatted_time, status))
        except Exception as e:
            print(f"Error extracting data from div: {e}")
    
    print('Num of transactions:' + str(i)) #Match this with rows in output.csv, if they are not equal means some transaction was not processed correctly (error).
    return records

# Function to write data to CSV
def write_data_to_csv(data, csv_file_path):
    with open(csv_file_path, mode='w', newline='') as file:
        writer = csv.writer(file, delimiter='|')
        writer.writerow(['Activity', 'Amount', 'Recipient', 'Account', 'Date','Time', 'Status'])
        writer.writerows(data)

# Sample HTML content (replace with actual HTML content)
with open('My Activity.html', 'r') as file:
    html_content = file.read()

# Extract data from the provided HTML content
data = extract_data_from_html(html_content)

# Write the extracted data to a CSV file
csv_file_path = 'output.csv'
write_data_to_csv(data, csv_file_path)

print(f"Data written to {csv_file_path}")
