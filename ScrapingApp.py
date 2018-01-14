# coding: UTF-8
import os
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

    # --------------------------
    # jsonファイルの存在チェック
    # --------------------------
    path = "./setting.json"

    if os.path.isfile(path) == 0:
        logger.error(path + "が見つかりません。")
        exit()

    # --------------------------
    # jsonファイルの読み込み
    # --------------------------

    json_file = open(path, 'r')
    dictionary = json.load(json_file)
    logger.info(dictionary)

    if "urls" not in dictionary:
        logger.error("jsonファイルにurlsが見つかりません。")
        exit()

    if "export_format" not in dictionary:
        logger.error("jsonファイルにexport_formatが見つかりません。")
        exit()

    logger.debug("ScrapingApp --- start ---")

    # --------------------------
    # 出力ファイルを開く
    # --------------------------

    now = datetime.datetime.now()
    export_file_name = "result_scraping_{0:%Y%m%d-%H%M%S}.txt".format(now)

    # --------------------------
    # jsonファイルの読み込み
    # --------------------------

    for url in dictionary['urls']:

        logger.info("## 走査するURL : " + url)
        o = urllib.parse.urlparse(url)
        if len(o.scheme) > 0:
            # html = urllib.request.urlopen(url).read()
            try:
                response = urllib.request.urlopen(url)
            except urllib.error.HTTPError as e:
                logger.info(e.reason)
                url = url + ' : ' + str(e.code)
                output_file_line('リクエストがエラーを返しました。', url, 'HTTPError')
                continue

            logger.info(response.getcode())
            if url != response.geturl():
                logger.info('redirect')
                response = urllib.request.urlopen(response.geturl())
                logger.info(str(response))
                logger.info(response.geturl())
                logger.info(response.getcode())
            html = response.read()
            url = url + ' : ' + str(response.getcode())

            soup = BeautifulSoup(html, "lxml")

            # --------------------------
            # id指定で抽出
            # --------------------------
            for id in dictionary['ids']:
                tags = soup.find_all(id=id)
                keyword = "id=" + id

                logger.info("--- " + keyword + " start --------------- ")

                if len(tags) <= 0:
                    output_file_line('対象が見つかりませんでした。', url, keyword)
                    logger.info("--- " + keyword + " end. 対象のタグが見つかりませんでした。   --------------- ")
                    continue

                # タグから文字列を抽出
                word_list = get_wordlist_from_tags(tags)
                # 文字列を出力
                export_message_from_list(word_list, url, keyword)

                logger.info("--- " + keyword + " end   --------------- ")

            # --------------------------
            # class指定で抽出
            # --------------------------
            for class_ in dictionary['classes']:
                tags = soup.find_all(class_=class_)
                keyword = "class=" + class_

                logger.info("--- " + keyword + " start --------------- ")

                if len(tags) <= 0:
                    output_file_line('対象が見つかりませんでした。', url, keyword)
                    logger.info("--- " + keyword + " end. 対象のタグが見つかりませんでした。   --------------- ")
                    continue

                # タグから文字列を抽出
                word_list = get_wordlist_from_tags(tags)
                # 文字列を出力
                export_message_from_list(word_list, url, keyword)

                logger.info("--- " + keyword + " end   --------------- ")

            # --------------------------
            # 属性指定で抽出
            # --------------------------
            for attr in dictionary['attrs']:
                # logger.info(attr)

                tags = soup.find_all(attrs=attr)
                keyword = "attrs=" + json.dumps(attr)

                logger.info("--- " + keyword + " start --------------- ")

                if len(tags) <= 0:
                    output_file_line('対象が見つかりませんでした。', url, keyword)
                    logger.info("--- " + keyword + " end. 対象のタグが見つかりませんでした。   --------------- ")
                    continue

                # タグから文字列を抽出
                word_list = get_wordlist_from_tags(tags)
                # 文字列を出力
                export_message_from_list(word_list, url, keyword)

                logger.info("--- " + keyword + " end   --------------- ")

            # --------------------------
            # タグと属性指定で抽出
            # --------------------------
            for target in dictionary['tags']:
                tag = target['tag']
                attr = target['attr']
                # logger.info(tag)
                # logger.info(attr)

                tags = soup.find_all(tag, attrs=attr)
                keyword = "tag=" + tag + " attrs=" + json.dumps(attr)

                logger.info("--- " + keyword + " start --------------- ")

                if len(tags) <= 0:
                    output_file_line('対象が見つかりませんでした。', url, keyword)
                    logger.info("--- " + keyword + " end. 対象のタグが見つかりませんでした。   --------------- ")
                    continue

                # タグから文字列を抽出
                word_list = get_wordlist_from_tags(tags)
                # 文字列を出力
                export_message_from_list(word_list, url, keyword)

                logger.info("--- " + keyword + " end   --------------- ")

        else:
            logger.info(url + "はURLではありません。")

    logger.debug("ScrapingApp --- end ---")


def get_wordlist_from_tags(tags):
    for target in tags:
        word_list = list(filter(lambda s: s != '', target.get_text().split('\n')))
        return word_list


def export_message_from_list(list, url, id):
    for word in list:
        output_file_line(word, url, id)


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
