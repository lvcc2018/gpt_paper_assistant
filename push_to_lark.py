"""
Code to render the output.json into a format suitable for a slackbot, and to push it to slack using webhooks
"""
import json
from datetime import datetime

from arxiv_scraper import Paper

from datetime import datetime

import requests

WEBHOOK_URL = (
    "https://open.feishu.cn/open-apis/bot/v2/hook/b3732b76-9d57-4fab-8e11-10635557b7b7"
)


class LarkBot:
    def __init__(self, secret=None) -> None:
        self.secret = secret

    def send(self, paper_dict) -> None:
        params = self.format_paper_context(paper_dict)
        resp = requests.post(url=WEBHOOK_URL, json=params)
        resp.raise_for_status()
        result = resp.json()
        if result.get("code") and result["code"] != 0:
            print(result["msg"])
            return
        print("消息发送成功")

    def format_paper_context(self, papers_dict):
        paper_list_all = []
        if len(papers_dict) == 0:
            return paper_list_all
        title_strings = [
            render_title(paper, i) for i, paper in enumerate(papers_dict.values())
        ]
        # paper_strings = [
        #     render_paper(paper, i) for i, paper in enumerate(papers_dict.values())
        # ]
        elements = [
            {
                "tag": "markdown",
                "content": f"**Personalized Daily Arxiv Papers {datetime.today().strftime('%m-%d-%Y')}**",
            },
            {
                "tag": "markdown",
                "content": f"Total relevant papers: **{str(len(title_strings))}**\nTable of contents with paper titles:",
            },
            {"tag": "hr"},
        ]
        for i in range(10):
            paper_name = title_strings[i]
            elements.append({"tag": "markdown", "content": f"**{i}.** {paper_name}"})
        elements.append(
            {
                "tag": "action",
                "actions": [
                    {
                        "tag": "button",
                        "text": {"tag": "plain_text", "content": "See it in Web"},
                        "type": "primary",
                        "multi_url": {
                            "url": "https://lvcc2018.github.io/gpt_paper_assistant/",
                            "pc_url": "",
                            "android_url": "",
                            "ios_url": "",
                        },
                    }
                ],
            }
        )
        lack_block_list = [
            [
                {
                    "config": {"wide_screen_mode": True},
                    "elements": elements,
                    "header": {
                        "template": "blue",
                        "title": {
                            "content": "Paper alert bot update on  ${time}",
                            "tag": "plain_text",
                        },
                    },
                }
            ]
        ]
        return lack_block_list


def render_title(paper_entry: Paper, counter: int) -> str:
    """
    :param counter: is the position of the paper in the list
    :param paper_entry: is a dict from a json. an example is
    {"paperId": "2754e70eaa0c2d40972c47c4c23210f0cece8bfc", "externalIds": {"ArXiv": "2310.16834", "CorpusId": 264451832}, "title": "Discrete Diffusion Language Modeling by Estimating the Ratios of the Data Distribution", "abstract": "Despite their groundbreaking performance for many generative modeling tasks, diffusion models have fallen short on discrete data domains such as natural language. Crucially, standard diffusion models rely on the well-established theory of score matching, but efforts to generalize this to discrete structures have not yielded the same empirical gains. In this work, we bridge this gap by proposing score entropy, a novel discrete score matching loss that is more stable than existing methods, forms an ELBO for maximum likelihood training, and can be efficiently optimized with a denoising variant. We scale our Score Entropy Discrete Diffusion models (SEDD) to the experimental setting of GPT-2, achieving highly competitive likelihoods while also introducing distinct algorithmic advantages. In particular, when comparing similarly sized SEDD and GPT-2 models, SEDD attains comparable perplexities (normally within $+10\\%$ of and sometimes outperforming the baseline). Furthermore, SEDD models learn a more faithful sequence distribution (around $4\\times$ better compared to GPT-2 models with ancestral sampling as measured by large models), can trade off compute for generation quality (needing only $16\\times$ fewer network evaluations to match GPT-2), and enables arbitrary infilling beyond the standard left to right prompting.", "year": 2023, "authors": [{"authorId": "2261494043", "name": "Aaron Lou"}, {"authorId": "83262128", "name": "Chenlin Meng"}, {"authorId": "2490652", "name": "Stefano Ermon"}], "ARXIVID": "2310.16834", "COMMENT": "The paper shows a significant advance in the performance of diffusion language models, directly meeting one of the criteria.", "RELEVANCE": 10, "NOVELTY": 8}, "2310.16779": {"paperId": "edc8953d559560d3237fc0b27175cdb1114c0ca5", "externalIds": {"ArXiv": "2310.16779", "CorpusId": 264451949}, "title": "Multi-scale Diffusion Denoised Smoothing", "abstract": "Along with recent diffusion models, randomized smoothing has become one of a few tangible approaches that offers adversarial robustness to models at scale, e.g., those of large pre-trained models. Specifically, one can perform randomized smoothing on any classifier via a simple\"denoise-and-classify\"pipeline, so-called denoised smoothing, given that an accurate denoiser is available - such as diffusion model. In this paper, we investigate the trade-off between accuracy and certified robustness of denoised smoothing: for example, we question on which representation of diffusion model would maximize the certified robustness of denoised smoothing. We consider a new objective that aims collective robustness of smoothed classifiers across multiple noise levels at a shared diffusion model, which also suggests a new way to compensate the cost of accuracy in randomized smoothing for its certified robustness. This objective motivates us to fine-tune diffusion model (a) to perform consistent denoising whenever the original image is recoverable, but (b) to generate rather diverse outputs otherwise. Our experiments show that this fine-tuning scheme of diffusion models combined with the multi-scale smoothing enables a strong certified robustness possible at highest noise level while maintaining the accuracy closer to non-smoothed classifiers.", "year": 2023, "authors": [{"authorId": "83125078", "name": "Jongheon Jeong"}, {"authorId": "2261688831", "name": "Jinwoo Shin"}], "ARXIVID": "2310.16779", "COMMENT": "The paper presents an advancement in the performance of diffusion models, specifically in the context of denoised smoothing.", "RELEVANCE": 9, "NOVELTY": 7}
    :return: a slackbot-appropriate mrkdwn formatted string showing the arxiv id, title, arxiv url, abstract, authors, score and comment (if those fields exist)
    """
    # get the arxiv id
    arxiv_id = paper_entry["arxiv_id"]
    # get the title
    title = paper_entry["title"]
    # get the arxiv url
    arxiv_url = f"https://arxiv.org/abs/{arxiv_id}"
    # get the authors
    authors = paper_entry["authors"]
    paper_string = (
        "<"
        + arxiv_url
        + "|*"
        + str(counter)
        + ". "
        + title.replace("&", "&amp;")
        + "*>\n"
    )
    paper_string += f'*Authors*: {", ".join(authors)}\n\n'
    return paper_string


def push_to_lack(papers_dict):
    lark_bot = LarkBot()
    lark_bot.send(papers_dict)


if __name__ == "__main__":
    # parse output.json into a dict
    with open("out/output.json", "r") as f:
        output = json.load(f)
    push_to_lack(output)
