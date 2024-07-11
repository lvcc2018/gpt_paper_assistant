"""
Code to render the output.json into a format suitable for a slackbot, and to push it to slack using webhooks
"""

import json
from datetime import datetime

import requests
import os

from openai import OpenAI

url = (
    "https://open.feishu.cn/open-apis/bot/v2/hook/b3732b76-9d57-4fab-8e11-10635557b7b7"
)

def get_abstract(abstract):
    OAI_KEY = os.environ.get("OAI_KEY")
    BASE_URL = os.environ.get("OAI_BASE_URL")
    prompt = "你是一个优秀的研究员，你的同事希望你能够用简短的话总结一下这个摘要的内容。请你写一下。"
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": abstract},
    ]
    client = OpenAI(
        # This is the default and can be omitted
        api_key=OAI_KEY,
        base_url=BASE_URL,
    )
    chat_completion = client.chat.completions.create(
        messages=messages,
        model="gpt-4o-2024-05-13",
    )

    return chat_completion.choices[0].message.content


class LarkBot:
    def __init__(self, secret=None) -> None:
        self.secret = secret

    def send(self, body) -> None:
        # body = self.format_paper_context(body)
        # body = json.dumps({"msg_type": "interactive", "card": body})
        # headers = {"Content-Type": "application/json"}
        # res = requests.post(url=url, data=body, headers=headers)
        # print(res)
        body = self.format_paper_context(body)
        content = {
            "type":"template",
            "data":{
                    "template_id": "AAqHnfDNDRgpr",    
                    "template_variable": body,
                }
            }
        body = json.dumps({"msg_type": "interactive", "card": json.dumps(content, ensure_ascii=False)})
        headers = {"Content-Type": "application/json"}
        res = requests.post(url=url, data=body, headers=headers)
        print(res)

    def format_paper_context(self, papers_dict):
        paper_list_all = []
        if len(papers_dict) == 0:
            return paper_list_all
        paper_info = [
            render_title(paper, i) for i, paper in enumerate(papers_dict.values())
        ]

        elements = []

        for i in range(len(paper_info)):
            paper_authors = ", ".join(paper_info[i][3])
            abstract = get_abstract(paper_info[i][2])
            # elements.append(
            #     {
            #         "tag": "markdown",
            #         "content": f"<text_tag >{i+1}</text_tag>**[{paper_info[i][0]}]({paper_info[i][1]})** \n<text_tag color='indigo'>Authors</text_tag>*<font color='blue'>{paper_authors}</font>*\n\n{abstract}",
            #         "text_align": "left",
            #         "text_size": "notation",
            #     }
            # )
            elements.append(
                {
                    "paperid": i+1,
                    "title": f"{paper_info[i][0]}",
                    "url": f"{paper_info[i][1]}",
                    "authors": paper_authors,
                    "abstract": abstract

                }
            )
        
        body = {
            "date": datetime.today().strftime('%m-%d-%Y'),
            "papers_count":len(paper_info),
            "papers": elements
            }

        # body = {
        #     "config": {"wide_screen_mode": True},
        #     "i18n_elements": {
        #         "zh_cn": [
        #             {
        #                 "tag": "repeat",
        #                 "variable": "papers",
        #                 "elements": [
        #                     {
        #                         "tag": "column_set",
        #                         "flex_mode": "stretch",
        #                         "background_style": "grey",
        #                         "horizontal_spacing": "8px",
        #                         "horizontal_align": "left",
        #                         "columns": [
        #                             {
        #                                 "tag": "column",
        #                                 "width": "weighted",
        #                                 "vertical_align": "top",
        #                                 "vertical_spacing": "8px",
        #                                 "background_style": "default",
        #                                 "elements": [
        #                                     {
        #                                         "tag": "column_set",
        #                                         "flex_mode": "none",
        #                                         "background_style": "default",
        #                                         "horizontal_spacing": "16px",
        #                                         "horizontal_align": "left",
        #                                         "columns": [
        #                                             {
        #                                                 "tag": "column",
        #                                                 "width": "weighted",
        #                                                 "vertical_align": "top",
        #                                                 "vertical_spacing": "8px",
        #                                                 "background_style": "default",
        #                                                 "elements": elements,
        #                                                 "weight": 1,
        #                                             }
        #                                         ],
        #                                     }
        #                                 ],
        #                                 "weight": 5,
        #                             }
        #                         ],
        #                     }
        #                 ],
        #             },
        #             {
        #                 "tag": "action",
        #                 "actions": [
        #                     {
        #                         "tag": "button",
        #                         "text": {"tag": "plain_text", "content": "查看更多"},
        #                         "type": "default",
        #                         "complex_interaction": True,
        #                         "multi_url": {
        #                             "url": "https://lvcc2018.github.io/gpt_paper_assistant/",
        #                             "pc_url": "",
        #                             "ios_url": "",
        #                             "android_url": "",
        #                         },
        #                     }
        #                 ],
        #             },
        #             {
        #                 "tag": "note",
        #                 "elements": [
        #                     {"tag": "plain_text", "content": "💡本栏目每天为你推荐论文"}
        #                 ],
        #             },
        #         ]
        #     },
        #     "i18n_header": {
        #         "zh_cn": {
        #             "title": {
        #                 "tag": "plain_text",
        #                 "content": f"{datetime.today().strftime('%m-%d-%Y')}   论文推送",
        #             },
        #             "subtitle": {
        #                 "tag": "plain_text",
        #                 "content": f"相关论文数：{len(paper_info)}   ",
        #             },
        #             "template": "blue",
        #             "ud_icon": {
        #                 "tag": "standard_icon",
        #                 "token": "table-group_outlined",
        #             },
        #         }
        #     },
        # }

        print(body)
        return body


def render_title(paper_entry, counter: int) -> str:
    """
    :param counter: is the position of the paper in the list
    :param paper_entry: is a dict from a json. an example is
    {"paperId": "2754e70eaa0c2d40972c47c4c23210f0cece8bfc",
    "externalIds": {"ArXiv": "2310.16834", "CorpusId": 264451832},
    "title": "Discrete Diffusion Language Modeling by Estimating the Ratios of the Data Distribution",
    "abstract": "Despite their groundbreaking performance for ... and enables arbitrary infilling beyond the standard left to right prompting.",
    "year": 2023,
    "authors":
        [
            {"authorId": "2261494043", "name": "Aaron Lou"},
            {"authorId": "83262128", "name": "Chenlin Meng"},
            {"authorId": "2490652", "name": "Stefano Ermon"}
        ],
    "ARXIVID": "2310.16834",
    "COMMENT": "The paper shows a significant advance in the performance of diffusion language models, directly meeting one of the criteria.", "RELEVANCE": 10,
    "NOVELTY": 8}
    :return: a slackbot-appropriate mrkdwn formatted string showing the arxiv id, title, arxiv url, abstract, authors, score and comment (if those fields exist)
    """
    # get the arxiv id
    arxiv_id = paper_entry["arxiv_id"]
    # get the title
    title = paper_entry["title"]
    # get the arxiv url
    arxiv_url = f"https://arxiv.org/abs/{arxiv_id}"
    # get the abstract
    abstract = paper_entry["abstract"]
    # get the authors
    authors = paper_entry["authors"]
    return [title, arxiv_url, abstract, authors]


def push_to_lark(papers_dict):
    lark_bot = LarkBot()
    lark_bot.send(papers_dict)


if __name__ == "__main__":
    # parse output.json into a dict
    with open("out/output.json", "r") as f:
        output = json.load(f)
    push_to_lark(output)
