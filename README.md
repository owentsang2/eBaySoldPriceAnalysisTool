# eBayPriceAnalysisTool

This Python script scrapes sold auction listings from eBay UK, saves the data into a CSV file, and generates visualizations for analysis.

![plot 1](https://github.com/user-attachments/assets/ecedec19-dc7f-4762-9810-f75884655dee)


![plot 2](https://github.com/user-attachments/assets/a90ec0e5-395e-4674-a28b-595b1a8d2bc7)

## Requirements
- Requests
- BS4 from BeautifulSoup
- Pandas
- datetime
- matplotlib.pyplot
- seaborn

### How to use
Download the .py file and adjust the script in VSCode or Jupyter and adjust the output, then run it.

### Notes
This script is for my project and is used for educational purposes and there are still limitations within this script.

## Customization
Customize the output file location by modifying the path in the output and df.read_csv() functions.
Adjust filtering criteria (e.g., excluding faulty or broken items) in the parse function.

## Acknowledgments
BeautifulSoup and Seaborn for facilitating web scraping and data visualization.

##Updates
I have now added more code using the help of chatGPT to help push my data automatically into PostgreSQL, here I can do more advanced queries and manipulations of the data to get better insights!
