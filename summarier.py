from bs4 import BeautifulSoup
from openai import OpenAI
from seleniumbase import SB
from dotenv import load_dotenv
import os
import argparse

load_dotenv()
OPEN_AI_KEY = os.getenv("OPEN_AI_KEY")

client = OpenAI(api_key=OPEN_AI_KEY)

def ai_analyze(title, content, comment_list):
    prompt = f"""
You are good at analyzing comments.
You will be provided an article and its comment written in korean.
HERE IS YOUR TASK:
- Translate the article title and content into Vietnamese.
- Summarize the most common opinions from the comments.
- For each opinion, give 2-3 examples of comments that express that opinion.

EXPECTED FORMAT BEGIN:
Title: ...
Content: ...
Comment:
- Opinion 1: Summary of the most common opinion
+ Comment
+ Comment
+ Comment
- Opinion 2: Summary of the second most common opinion
+ Comment
+ Comment
...
EXPECTED FORMAT END

TITLE: {title}
CONTENT: 
{content}

COMMENT LIST:
{comment_list}
"""
    
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": prompt}
        ]
    )

    print(completion.choices[0].message.content)



def extract_comments(html):
    soup = BeautifulSoup(html, 'html.parser')
    comments = soup.find_all("li", class_="fdb_itm clear")
    comment_list = """"""
    count = 0
    for comment in comments:
        if count == 50:
            break
        text = comment.find("div", class_="xe_content").get_text(separator="\n", strip=True)
        comment_list += f"{count}. "+ text + "\n"
        count += 1
    return comment_list,count

def extract_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    title = soup.find(class_="title").get_text(separator="\n", strip=True)
    content = soup.find(class_="rd_body").get_text(separator="\n", strip=True)
    return title, content



def main():
    if OPEN_AI_KEY is None:
        print("Please provide the OPEN_AI_KEY in .env file")
        return
    
    parser = argparse.ArgumentParser(description="Process an article ID parameter.")
    parser.add_argument('--id', type=str, required=True, help="The article ID to process.")
    
    args = parser.parse_args()

    with SB(uc=True, headless=True) as sb:
        sb.open(f'https://theqoo.net/hot/{args.id}')

        html = sb.get_page_source()

        title, content = extract_content(html)
        comments, count = extract_comments(html)
        
        while(count < 50):
            try:
                sb.click('.show_more')
                html = sb.get_page_source()
                comments, count = extract_comments(html)
            except Exception as e:
                print(e)
                break
        ai_analyze(title, content, comments)

if __name__ == "__main__":
    main()