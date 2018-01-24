# coding: UTF-8
import os
import time
import json
import logging
import datetime
import urllib.parse
import urllib.request
from bs4 import BeautifulSoup

LOG_LEVEL = 'INFO'

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s [%(levelname)s] %(module)s | %(message)s',
    datefmt='%Y/%m/%d %H:%M:%S',
)
logger = logging.getLogger(__name__)


def main():
    global dictionary
    global export_file_name
    global target_word

    global sleep_time
    global domain

    # --------------------------
    # jsonファイルの存在チェック
    # --------------------------
    path = "./setting_crawl.json"

    if os.path.isfile(path) == 0:
        logger.error(path + "が見つかりません。")
        exit()

    # --------------------------
    # jsonファイルの読み込み
    # --------------------------

    json_file = open(path, 'r')
    dictionary = json.load(json_file)
    logger.info(dictionary)

    if "target_url" not in dictionary:
        logger.error("jsonファイルにtarget_urlが見つかりません。")
        exit()

    if "export_format" not in dictionary:
        logger.error("jsonファイルにexport_formatが見つかりません。")
        exit()

    sleep_time = 10
    if "sleep_second" in dictionary:
        sleep_time = dictionary['sleep_second']

    target_word = ""
    # if "target_word" in dictionary:
    #     target_word = dictionary['target_word'].decode("utf-8")

    logger.debug("CrawlApp --- start ---")

    # --------------------------
    # 出力ファイルを開く
    # --------------------------

    now = datetime.datetime.now()
    export_file_name = "result_crawl_{0:%Y%m%d-%H%M%S}.txt".format(now)

    # --------------------------
    # jsonファイルの読み込み
    # --------------------------

    # URLをパースする
    parsed_url = urllib.parse.urlparse(dictionary['target_url'])

    if len(parsed_url.scheme) > 0:

        netloc = parsed_url.netloc

        logger.info("##### クロールするURL : " + dictionary['target_url'])
        logger.info("####  クロールするドメイン : " + netloc)

        request_crawl(dictionary['target_url'], netloc)

    else:
        logger.info(url + "はURLではありません。")

    logger.info("CrawlApp --- end ---")


def request_crawl(url, domain):
    logger.info(urllib.parse.urljoin(domain, url) + "は。")

    # URL判定 (絶対 or 相対)
    parsed_url = urllib.parse.urlparse(url)

    if len(parsed_url.scheme) > 0:
        # 絶対の場合

        if url.find(domain) > -1:
            # 対象のドメイン : GO
            request_url(url, domain)

        else:
            # 対象外のドメイン : SKIP
            logger.info(url + "は対象のドメインではありません。")

    else:
        # 相対の場合
        # ドメインをくっつけてGO
        logger.info(url)
        join_url = urllib.parse.urljoin(domain, url)
        logger.info(join_url)
        logger.info(domain)
        request_url(join_url, domain)


def request_url(url, domain):
    global sleep_time

    # Dos攻撃にならないように
    time.sleep(sleep_time)

    try:
        output_file_line('', url, '')
        response = urllib.request.urlopen(url)
        html = response.read()
        soup = BeautifulSoup(html, "lxml")

        links = [a.get("href") for a in soup.find_all("a")]
        for l in links: request_crawl(l, domain)

    except urllib.error.HTTPError as e:
        logger.info(e.reason)
        url = url + ' : ' + str(e.code)
        output_file_line('リクエストがエラーを返しました。', url, 'HTTPError')


def output_file_line(word, url, id):
    global dictionary
    global export_file_name

    word = word.encode('cp932', "ignore").decode('cp932').strip()
    logger.info(dictionary['export_format'].format(url=url, id=id, word=word))
    f = open('./logs/' + export_file_name, 'a')
    f.write(dictionary['export_format'].format(url=url, id=id, word=word) + '\n')
    f.close()


if __name__ == '__main__':
    main()
