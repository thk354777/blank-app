import streamlit as st
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain import hub
# from google.colab import userdata
from openai import OpenAI
import time
from langchain.chains.combine_documents import create_stuff_documents_chain
import chromadb
# from chromadb.config import Settings
# from langchain_community.vectorstores import Chroma
# from langchain.chat_models import ChatOpenAI #comment?
from langchain_community.chat_models import ChatOpenAI
from openai import OpenAI as TyphoonClient
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.chains import ConversationChain
from langchain.memory.summary import ConversationSummaryMemory
from langchain_core.messages import HumanMessage, AIMessage
from langchain.schema import HumanMessage
# from langchain.embeddings import HuggingFaceEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings

from dotenv import load_dotenv
import os

from sentence_transformers import SentenceTransformer
import torch
from transformers import AutoTokenizer
import pysqlite3 as sqlite3
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
# torch.cuda.empty_cache()

load_dotenv()
# typhoon_api_key = os.getenv("TYPHOON_API_KEY")
# os.environ["TYPHOON_API_KEY"] = os.getenv("TYPHOON_API_KEY")
# TYPHOON_API_KEY=os.getenv("TYPHOON_API_KEY")
# os.environ["OPENAI_API_KEY"] = TYPHOON_API_KEY
# os.environ["OPENAI_API_BASE"] = "https://api.opentyphoon.ai/v1"

# TYPHOON_API_KEY = os.environ.get("TYPHOON_API_KEY")
# os.environ["OPENAI_API_KEY"] = os.environ.get("TYPHOON_API_KEY")
# ty = st.secrets["TYPHOON_API_KEY"]
st.secrets.key = 'TYPHOON_API_KEY'
ty = st.secrets.key
# os.environ["OPENAI_API_KEY"] = st.secrets["TYPHOON_API_KEY"]
# os.environ["OPENAI_API_BASE"] = "https://api.opentyphoon.ai/v1"
doc = [
  {
    "disease": "ไข้หวัดใหญ่",
    "symptoms": [
      '''ไข้สูง ปวดเมื่อยตามตัว'''
    ],
    "treatment": [
      '''การให้ยาต้านไวรัส amantadine hydrochloride หรือยา rimantidine hydrochloride ภายใน 48 ชั่วโมง นาน 3-5 วัน จะช่วยลดอาการและจำนวนเชื้อไวรัสชนิด A ในสารคัดหลั่งที่ทางเดินหายใจได้ ขนาดยาที่ใช้ในเด็กอายุ 1-9 ปี ให้ขนาด 5 มก./กก./วัน แบ่งให้ 2 ครั้ง สำหรับผู้ป่วยอายุ 9 ปีขึ้นไปให้ขนาด 100 มก. วันละ 2 ครั้ง (แต่ถ้าผู้ป่วยน้ำหนักน้อยกว่า 45 กก. ให้ใช้ขนาดเดียวกับเด็กอายุ 1-9 ปี) นาน 2-5 วัน สำหรับผู้ป่วยอายุ 65 ปีขึ้นไป หรือผู้ที่การทำงานของตับและไตผิดปกติ ต้องลดขนาดยาลง
ในช่วงหลังๆ ของการรักษาด้วยยาต้านไวรัส อาจพบการดื้อยาตามด้วยการแพร่โรคไปยังคนอื่นได้ กรณีนี้อาจต้องให้ยาต้านไวรัสแก่ผู้เสี่ยงโรคสูงที่อยู่รวมกันเป็นกลุ่ม ถ้ามีอาการแทรกซ้อนจากเชื้อแบคที เรียต้องให้ยาปฏิชีวนะด้วย และควรหลีกเลี่ยงยาลดไข้พวก salicylates เพื่อลดความเสี่ยงต่อการเกิดโรค Reye's syndrome และ 3-5 วัน อาการดีขึ้น'''
    ]
  },
  {
    "disease": "ไข้หวัดธรรมดา",
    "symptoms": [
      "ไอแห้ง"
    ],
    "treatment": [
      "การใช้ยาแก้ปวดลดไข้ (พาราเซตามอล หรือ ไอบูโพรเฟน) การใช้ยาแก้คัดจมูก หรือยาแก้ไอ รวมถึงการพักผ่อนให้เพียงพอ ดื่มน้ำมากๆ และทานอาหารที่มีประโยชน์ และ 2-3 วันอาการดีขึ้น"
    ]
  },
  {
    "disease": "ปอดติดเชื้อ",
    "symptoms": [
      "ไข้สูง เหนื่อย ไอมีเสมหะ"
    ],
    "treatment": [
      "วิธีการรักษาโรคปอดขึ้นอยู่กับชนิดของเชื้อโรค หากเป็นการติดเชื้อไวรัสโดยส่วนใหญ่ไม่มียารักษาจำเพาะจะเป็นการรักษาตามอาการ เป็นการรักษาประคับประคองจนกว่าพยาธิสภาพของปอดจะดีขึ้น ยกเว้น ไวรัสไข้หวัดใหญ่ ซึ่งมียาต้านไวรัสในรูปแบบรับประทานเป็นเวลา 5 วัน ส่วนการติดเชื้อแบคทีเรียในปอดสิ่งสำคัญคือการใช้ยาฆ่าเชื้อให้ตรงกับเชื้อเป็นหลัก โดยเฉพาะปอดติดเชื้อจากการติดเชื้อในกระแสเลือด หากได้รับยาฆ่าเชื้ออย่างทันท่วงที ก็จะทำให้มีอัตราการรอดชีวิตที่สูงมาก ดังนั้นควรเฝ้าสังเกตอาการผิดปกติให้ดี หากมีอาการผิดปกติควรรีบมาพบแพทย์ เพื่อลดความเสี่ยงอันตรายที่อาจเกิดขึ้น"
    ]
  },
  {
    "disease": "ท้องเสีย",
    "symptoms": [
      "ปวดท้อง คลื่นไส้อาเจียน ถ่ายเหลว มีไข้ได้"
    ],
    "treatment": [
      """รักษาตามอาการ โดยเฉพาะอาการปวดท้อง ไม่แนะนำการให้ยาปฏิชีวนะ ยกเว้นในกรณี severe ill patients, traveler&#39;s diarrhea, septicemic prone conditions e.g. cirrhosis, uncontrolled diabetes mellitus immunocompromised hosts
ในผู้ใหญ๋ให้

Tetracycline 500 มก.วันละ 4 ครั้ง นาน 3 วัน
Doxycycline 100 มก.วันละ 2 ครั้ง นาน 3 วัน
Norfloxacin 400 มก.วันละ 2 ครั้ง นาน 3 วัน
ในเด็กที่มีอาการรุนแรง

Tetracycline 25-50 มก./กก/วัน
Norfloxacin 10-20 มก./กก/วัน
Cotrimoxazole (trimetroprim) 10 มก./กก/วัน"""
    ]
  },
  {
    "disease": "ไส้ติ่งแตก",
    "symptoms": [
      "ปวดขวาล่าง ไข้ เบื่ออาหาร คลื่นไส้ อาเจียน"
    ],
    "treatment": [
      "การประเมินภาวะทั่วไปและให้การดูแลเรื่องภาวะช็อกด้วยการให้สารน้ำทางหลอดเลือดดำควบคู่กับการให้ยาปฏิชีวนะขยายสเปกตรัมเพื่อควบคุมการติดเชื้อในช่องท้อง จากนั้นจึงเข้าสู่กระบวนการผ่าตัดเอาไส้ติ่งออก (emergency appendectomy) พร้อมกับล้างทำความสะอาดช่องท้อง หากพบมีฝีหนองอาจต้องใส่ท่อระบาย (percutaneous drainage) ร่วมด้วย เมื่อตัดไส้ติ่งเสร็จแล้วแพทย์จะเฝ้าสังเกตอาการภายหลังผ่าตัด โดยให้ยาปฏิชีวนะต่อจนแน่ใจว่าไม่มีการติดเชื้อซ้ำ และส่งเสริมการฟื้นฟูด้วยการรับประทานอาหารอ่อน ยาแก้ปวด และการเคลื่อนไหวเบา ๆ อย่างปลอดภัย โดยผู้ป่วยส่วนใหญ่จะฟื้นตัวดีภายใน 1–2 สัปดาห์ (ควรติดตามผลการรักษาตามคำแนะนำแพทย์อย่างเคร่งครัด)"
    ]
  }
]

doc_extra = [
{
        "disease": "โบทูลิซึม",
        "symptoms": [
            "หนังตาตก การมองเห็นไม่ชัด เห็นเป็นสองภาพ ปากแห้ง เจ็บคอ กล้ามเนื้อสองข้างอ่อนแรงเท่ากัน อาเจียน ท้องเดิน"
            ],
        "treatment": [
            "การรักษาด้วยการช่วยหายใจและให้สารต้านพิษโดยเฉพาะ จะช่วยลดอัตราป่วยตายในระยะที่หาย การฟื้นตัวจะค่อนข้างช้า (เป็นเดือนหรือในบางรายเป็นปี) การวินิจฉัยกระทำได้โดยตรวจพบสารพิษเฉพาะในน้ำเหลืองหรืออุจจาระของผู้ป่วยหรือการเพาะเชื้อพบ Clostridium botulinum"
            ]
    },
    {
        "disease": "พยาธิช่องคลอด",
        "symptoms": [
            "ผู้หญิงจะมีตกขาวผิดปกติ มีสีเหลืองออกเขียว อาจมีกลิ่น อาจเจ็บปวดเวลาร่วมเพศ คัน แสบ และระคายเคืองบริเวณอวัยวะเพศ ผู้ชายจะมีอาการคล้ายหนองในเทียม แสบเวลาปัสสาวะ ปวดอัณฑะ อักเสบที่หนังหุ้มปลายองคชาต มีมูกใสออกมาทางท่อปัสสาวะ"
            ],
        "treatment": [
            "การรับประทานยา โดยแพทย์จะทำการจ่ายยาปฏิชีวนะให้ผู้ป่วยนำไปรับประทานต่อเนื่องกันเป็นเวลา 7-10 วัน"
            ]
    },
    {
        "disease": "มือเท้าปาก",
        "symptoms": [
            "ปวดศีรษะ คลื่นไส้ ปวดเมื่อย มีไข้ร่วมกับตุ่มเล็กๆ เกิดขึ้นที่ผิวหนังบริเวณฝ่ามือ ฝ่าเท้าและในปาก ไข้สูง ไข้ต่ำ เจ็บในปาก กลืนน้ำลายไม่ได้ พบตุ่มแผลในปากส่วนใหญ่พบที่เพดานอ่อนลิ้น กระพุ้งแก้ม อาจมี 1 แผล หรือ 2-3 แผล ขนาด 4-8 มิลลิลิตร น้ำลายไหล พบตุ่มพอง สีขาวขุ่นบนฐานรอบสีแดง ขนาด 3-7 มิลลิเมตร บริเวณด้านข้างของนิ้วมือ นิ้วเท้า บางครั้งพบที่ฝ่ามือ ฝ่าเท้า ส้นเท้า ส่วนมากมีจำนวน 5-6 ตุ่ม"
            ],
        "treatment": [
            "รักษาตามอาการ ให้ยาลดไข้ แก้ปวด ทายาที่ลดอาการปวดในรายที่มีแผลที่ลิ้นหรือกระพุ้งแก้ม แต่ในกรณีผู้ป่วยมีอาการแทรกซ้อนรุนแรง ต้องรับไว้รักษาเป็นผู้ป่วยใน เช่น รับประทานอาหารหรือนมไม่ได้ มีอาการสมองอักเสบเยื่อหุ้มสมองอักเสบ ภาวะปอดบวมน้ำ กล้ามเนื้อหัวใจอักเสบ กล้ามเนื้ออ่อนแรงคล้ายโปลิโอ จำเป็นต้องให้การรักษาแบบ intensive care และดูแลโดยผู้เชี่ยวชาญ"
            ]
    },
    {
        "disease": "เยื่อหุ้มสมองอักเสบ",
        "symptoms": [
            "ปวดศีรษะ คอแข็งขยับไม่ได้ ไข้ คลื่นไส้ อาเจียน ชัก แพ้แสงหรือไวต่อแสง ไม่มีความกระหายหรืออยากอาหาร ปวดหัวอย่างรุนแรงผิดปกติ ง่วงนอน หรือตื่นนอนยาก ผิวหนังเป็นผื่น เด็กแรกเกิดจนกระทั่งอายุไม่เกิน 1 เดือน มีอาการ ร้องไห้ตลอดเวลา มีไข้สูง ตัวและลำคอแข็ง นอนหลับมากเกินไป หรือหงุดหงิดง่าย เฉื่อยชา เคลื่อนไหวน้อย กระหม่อมนูน ดื่มนมได้น้อยลงมาก"
            ],
        "treatment": [
            "การรักษาโรคเยื่อหุ้มสมองอักเสบจากแบคทีเรียวิธีรักษาเยื่อหุ้มสมองอักเสบจากแบคทีเรียคือให้ยาปฏิชีวนะทางหลอดเลือดดำ นอกจากยาปฏิชีวนะแล้ว ในผู้ป่วยบางราย แพทย์อาจให้ยาคอร์ติโคสเตียรอยด์ เช่น เดกซาเมทาโซน เพื่อบรรเทาอาการอักเสบที่เกิดจากแบคทีเรีย ทั้งนี้ ผู้ป่วยที่มีอาการเฉียบพลันอาจจำเป็นต้องได้รับยาคอร์ติโคสเตียรอยด์หรือยาปฏิชีวนะทางหลอดเลือดดำอย่างเร่งด่วน", "การรักษาโรคเยื่อหุ้มสมองอักเสบจากไวรัส ส่วนมาก โรคเยื่อหุ้มสมองอักเสบจะดีขึ้นเองในไม่กี่สัปดาห์ ผู้ป่วยที่มีอาการไม่รุนแรงอาจปฏิบัติดังนี้เพื่อให้อาการหายเร็วขึ้น พักผ่อนเยอะ ๆ ดื่มน้ำมาก ๆ รับประทานยาแก้ปวดเพื่อบรรเทาอาการปวดตัวหรือลดไข้ อย่าลืมว่ายาปฏิชีวนะใช้รักษาเยื่อหุ้มสมองอักเสบจากไวรัสไม่ได้ ทั้งนี้ แพทย์อาจจ่ายยาคอติโคสเตียรอยด์ให้เพื่อลดอาการบวมในสมอง และจ่ายยาเพื่อควบคุมอาการชัก สำหรับผู้ที่เป็นเยื่อหุ้มสมองจากไวรัสเฮอร์ปีส์หรือไวรัสไข้หวัดใหญ่ อาจได้ยาต้านไวรัสมารับประทาน", "โรคเยื่อหุ้มสมองอักเสบประเภทอื่น ๆ สำหรับโรคเยื่อหุ้มสมองอักเสบเรื้อรัง วิธีรักษาจะพิจารณาตามสาเหตุที่ก่อให้เกิดโรค ขณะที่ยาต้านไวรัสช่วยรักษาเยื่อหุ้มสมองอักเสบจากเชื้อราได้ ในบางเคสอาจไม่จำเป็นต้องรักษา เพราะอาการจะหายไปเอง สำหรับเยื่อหุ้มสมองที่สัมพันธ์กับมะเร็ง แพทย์จะทำการรักษามะเร็งชนิดนั้น ๆ และสำหรับเยื่อหุ้มสมองอักเสบที่เกิดจากอาการแพ้หรือโรคภูมิคุ้มกันทำลายตนเอง แพทย์อาจรักษาด้วยการให้ยาคอติโคสเตียรอยด์หรือยากดภูมิอื่น ๆ"
            ]
    },
    {
        "disease": "โรคเรื้อน",
        "symptoms": [
            "ผิวหนังแห้ง ผิวหนังสีจางหรือเข้มข้นกว่าผิวหนังปกติ ขนร่วง เหงื่อไม่ออก ผิวหบังชา หยิกไม่เจ็บ ไม่คัน ผื่นนูนแดงหนา ตุ่มแดงไม่คันที่ใบหูจะนูนหนา ขนคิ้วร่วง ผื่นรูปวงแหวนหรือแผ่นนูนแดง ขอบเขตผื่นชัดเจน"
            ],
        "treatment": [
            "โรคเรื้อนสามารถรักษาให้หายขาดได้โดยกินยาติดต่อกันเป็นเวลา 6 เดือน หรือ 2 ปี แล้วแต่ชนิดของโรค หากพบว่าทีรอยโรคที่ผิวหนัง มีอาการชา หรือเป็นโรคผิวหนังเรื้อรังใช้ยากิน ยาทา 3 เดือนแล้วไม่หายให้สงสัยว่าอาจเป็นโรคเรื้อน ควรรีบไปพบแพทย์"
            ]
    },
    {
        "disease": "โรคความดันโลหิตสูง",
        "symptoms": [
            "ปวดศีรษะ มึนงง เวียนศีรษะ หนื่อยง่าย ภาวะแทรกซ้อนอาจทำให้เกิดเลือดออกที่จอตา ประสาทตาเสื่อม ตามัว หรือ ตาบอดได้ หัวใจเต้นผิดจังหวะ "
            ],
        "treatment": [
            "การให้ยาลดความดันโลหิตให้อยู่ในเกณฑ์มาตรฐาน สามารถลดภาวะแทรกซ้อนที่เกิดจากความดันโลหิตสูงได้ นอกจากการรับประทานยาแล้ว ผู้ป่วยความดันโลหิตสูงทุกรายควรจะได้มีการปรับเปลี่ยนพฤติกรรมหรือการรักษาความดันโลหิตสูงโดยไม่ต้องใช้ยาร่วมด้วย ดังนี้ ออกกำลังกายแบบแอโรบิก หมายถึงการออกกำลังกาย ที่มีการเคลื่อนไหวร่างกายตลอดเวลา เช่น วิ่ง เดินเร็ว ว่ายนํ้า อย่างสม่ำเสมอ อย่างน้อย วันละ 15-30 นาที 3-6 วันต่อสัปดาห์ และการควบคุมน้ำหนักให้อยู่ในเกณฑ์ปกติ ลดปริมาณแอลกอฮอล์ให้อยู่ในเกณฑ์เหมาะสม งดบุหรี่ ลดเครียด รับประทานอาหารที่มีคุณภาพ โดยการลดอาหารเค็มจัด ลดอาหารมัน เพิ่มผักผลไม้ เน้นอาหารพวกธัญพืช ปลา นมไขมันต่ำ ถั่ว รับประทานอาหารที่มีไขมันอิ่มตัวต่ำ หลีกเลี่ยงเนื้อแดง น้ำตาล เครื่องดื่มที่มีรสหวานจะทำให้ระดับความดันโลหิตลดลงได้ ปรึกษาแพทย์เกี่ยวกับยาที่ใช้อยู่เพราะมียาบางตัวทำให้ความดันโลหิตสูงขึ้นได้ ปรึกษาแพทย์ถ้าต้องใช้ยาคุมกำเนิด"
            ]
    },
    {
        "disease": "โรคหัด",
        "symptoms": [
            "ไข้ ตัวร้อน น้ำมูกไหล ไอบ่อย เจ็บคอ ตาเยิ้มแดง และมีตุ่มคอพลิค ตุ่มแดงที่มีสีขาวเล็ก ๆ ตรงกลางขึ้นในกระพุ้งแก้ม ผื่นขึ้นตามร่างกาย ผื่นแดงหรือสีแดงออกน้ำตาลขึ้นเป็นจุดบนหน้าผาก ที่ใบหน้า ลำคอ หน้าผาก มือและเท้า"
            ],
        "treatment": [
            "ผู้ป่วยสามารถดูแลตัวเองให้อาการทุเลาลงได้ด้วยการดื่มน้ำวันละ 6-8 แก้ว พักผ่อนให้เพียงพอเพื่อเสริมภูมิคุ้มกันร่างกาย อยู่ในที่แห้งอุณหภูมิพอเหมาะเพื่อลดอาการไอบ่อยและเจ็บคอ และอาจให้วิตามินเอเสริมให้กับร่างกาย ผู้ป่วยส่วนใหญ่จะมีอาการดีขึ้นภายใน 2 สัปดาห์ อย่างไรก็ดี แพทย์อาจสั่งจ่ายยาลดไข้ที่ไม่ใช่ยาแอสไพรินอย่างยาไอบูโพรเฟน (Ibuprofen) และยาพาราเซตามอล (Paracetamol) เพื่อช่วยลดไข้และบรรเทาอาการปวดกล้ามเนื้อ นอกจากนี้ ผู้ป่วยโรคหัดที่เริ่มมีผื่นขึ้นควรอยู่ในบ้าน ไม่ไปโรงเรียน ทำงาน หรือพบปะผู้คนตามที่สาธารณะเป็นเวลาอย่างน้อย  4 วันหลังจากผื่นเริ่มปรากฏเพื่อป้องกันการแพร่เชื้อไปยังผู้คนรอบข้าง หากทารก เด็ก ผู้ที่ป่วยเป็นวัณโรค มะเร็ง หรือโรคอื่น ๆ ที่ทำให้ระบบภูมิคุ้มกันร่างกายอ่อนแอได้รับเชื้อไวรัสโรคหัด ควรรีบไปพบแพทย์เพื่อรับการดูแลอย่างใกล้ชิดทันที ที่สำคัญ ไม่ควรให้เด็กอายุต่ำกว่า 12  ปีที่ติดเชื้อไวรัสดังกล่าวรับประทานยาแอสไพรินเพื่อลดไข้ เพราะเด็กอาจจะเกิดอาการแพ้ยาที่เรียกว่ากลุ่มอาการราย (Reye’s Syndrome) ซึ่งทำให้ตับและสมองบวม เมื่อเกิดอาการดังกล่าว เด็กจะอาเจียนทันที อ่อนเพลีย หมดความสนใจต่อสิ่งรอบตัว พูดหรือทำอะไรที่แปลกไปจากเดิม และมักนอนซม หากตับและสมองถูกทำลายไปเรื่อย ๆ เด็กจะเกิดอาการสับสนมึนงง หายใจหอบเร็ว แสดงพฤติกรรมก้าวร้าว เกิดอาการชัก และหมดสติ ซึ่งหากได้รับการวินิจฉัยและรักษาอย่างทันท่วงที ก็อาจหายจากอาการได้อย่างปลอดภัย"
            ]
    },
    {
        "disease": "โรควัณโรคปอด",
        "symptoms": [
            "ต่อมน้ำเหลืองโตที่ขั้วปอด ที่คอ และที่อื่นๆ ไข้ต่ำ ไข้ เบื่ออาหาร น้ำหนักตัวลดลง ไอเรื้อรัง เจ็บหน้าอก เหนื่อยหอบ มีน้ำในช่องเยื่อหุ้มปอด ปวดศีรษะ อาเจียน คอแข็ง ชัก ซึม"
            ],
        "treatment": [
            "การรักษาจะให้ยาร่วมกันอย่างน้อย 3 ชนิด เพื่อลดอัตราการดื้อยา และเพิ่มประสิทธิภาพของยา ยาที่ใช้ได้แก่ Streptomycin, Pyrazinamide, Rifampin, Isoniacid, Ethambutol การรักษาจะได้ผลดีถ้ามารับการรักษาเสียแต่ระยะเริ่มแรก และจะต้องกินยาอย่างสม่ำเสมอเป็นระยะเวลาอย่างน้อย 6 เดือน และจะต้องดูแลให้พักผ่อนและให้อาหารที่มีโปรตีนสูงและมีไวตามิน เพื่อช่วยเพิ่มความต้านทานโรค"
            ]
    },
    {
        "disease": "หนองใน",
        "symptoms": [
            "ผู้ชายจะมีอาการปัสสาวะขัด แสบ หนองไหลจากท่อปัสสาวะ อาจมีอาการแทรกซ้อน ฝีที่ปากท่อปัสสาวะ ฝีที่ผนังท่อปัสสาวะ ท่อปัสสาวะตีบตัน ผู้หญิงจะมีอาการตกขาว อักเสบที่ท่อปัสสาวะ ปัสสาวะแสบขัด"
            ],
        "treatment": [
            "การรักษาทำได้โดยการฉีดยาปฏิชีวนะ หากอาการไม่ดีขึ้น ควรกลับมาพบแทย์ทันทีเนื่องจากเชื้ออาจดื้อยา ผู้ป่วยควรงดมีเพศสัมพันธ์อย่างน้อย 7 วันหลังเข้ารับการรักษาเพื่อป้องกันการแพร่เชื้อ เนื่องจากผู้ป่วยจะมีความเสี่ยงต่อการเป็นโรคติดต่อทางเพศสัมพันธ์อื่น ๆ ด้วย  แนะนําให้ไปพบแพทย์เพื่อตรวจติดตามหลังการรักษา และ 3 เดือนหลังจากได้รับการรักษาเพื่อทำการตรวจคัดกรองโรคติดต่อทางเพศสัมพันธ์อื่น ๆ"
            ]
    },
    {
        "disease": "อีโบล่า",
        "symptoms": [
            "ไข้สูง อ่อนเพลีย ปวดกล้ามเนื้อ ปวดศีรษะ เจ็บคอ ท้องเสีย อาเจียน ผื่น ไตและตับไม่ทำงาน มีเลือดออกทั้งภายในและภายนอก "
            ],
        "treatment": [
            "การรักษายังไม่มีการรักษาเฉพาะรวมทั้งยังไม่มีวัคซีน การทดแทนน้ำ-เกลือแร่ให้เพียงพอ"
            ]
    }
]


doc.extend(doc_extra)
documents = [Document(page_content=d["symptoms"][0], metadata={"disease": d["disease"]}) for d in doc]

model_path = "Snowflake/snowflake-arctic-embed-l-v2.0"

embeddings = HuggingFaceEmbeddings(
    model_name=model_path,
    model_kwargs={"device": "cpu"}
)


import shutil
import os
import stat
import gc
import datetime

# ------------ Configuration ------------
base_directory = 'docs/chroma4'
collection_name = "my_collection13"

# ------------ Safe Delete Handler ------------
def on_rm_error(func, path, exc_info):
    # fallback ถ้าไฟล์ถูกล็อกโดย OS (Windows)
    import stat
    os.chmod(path, stat.S_IWRITE)
    func(path)

def safe_reset_chroma(base_directory, collection_name, vectordb=None):
    # ปิด vectordb (ถ้ามี)
    if vectordb:
        vectordb._collection = None
        vectordb = None
        gc.collect()
        time.sleep(1)

    # ลบ collection เดิม (ถ้ามี)
    client = chromadb.Client()
    try:
        client.delete_collection(collection_name)
        print(f"✅ Deleted Chroma collection: {collection_name}")
    except Exception as e:
        print(f"ℹ️ Skipped collection deletion (maybe not exists): {e}")

    # สร้างโฟลเดอร์ใหม่ตาม timestamp
    now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    new_persist_directory = os.path.join(base_directory, f"chroma_{now}")
    os.makedirs(new_persist_directory, exist_ok=True)
    print(f"📁 Created new persist directory: {new_persist_directory}")

    # รอระบบเคลียร์หน่วยความจำ
    gc.collect()
    time.sleep(1)

    # return client และ path ใหม่
    return client, new_persist_directory

# ------------ เรียกใช้ฟังก์ชัน ------------
# safe_reset_chroma(persist_directory, collection_name)
# shutil.rmtree(persist_directory, ignore_errors=True)
# shutil.rmtree(persist_directory, onerror=on_rm_error)

# ------------ สร้าง client และ collection ใหม่ ------------
# client = chromadb.Client()
# client = safe_reset_chroma(persist_directory, collection_name)
client, persist_directory = safe_reset_chroma(base_directory, collection_name)
collection = client.create_collection(
    name=collection_name,
    metadata={"hnsw:space": "cosine"}
)

vectordb = Chroma.from_documents(
    documents=documents,
    collection_name=collection_name,
    embedding=embeddings,
    persist_directory=persist_directory
)

llm = ChatOpenAI(
    model_name="typhoon-v2-70b-instruct", #"typhoon-v2.1-12b-instruct", "typhoon-v2-70b-instruct"
    temperature=0.9,
    max_tokens=512, # Total Context Window 8k เป็น token input + token output แล้ว
    openai_api_key=os.environ["OPENAI_API_KEY"],
    openai_api_base="https://api.opentyphoon.ai/v1",
)

conversaton_sum = ConversationChain(
    llm=llm,
    memory=ConversationSummaryMemory(llm=llm)
)

template = """
You are an AI medical assistant. Use the provided context to answer user questions about symptoms and assess possible conditions based on the available data.

Safety Requirements:
Do not diagnose any disease or recommend treatments beyond the information provided.

Only respond based on the provided context.

If the information is insufficient, clearly state that a score cannot be provided and suggest follow-up questions to ask the user.

Always encourage the user to consult a physician, especially if symptoms are severe or persistent.

Response Guideline:

Analyze the user's symptoms from their question and the content given. If any disease has symptoms that clearly do not match (e.g., pain in the wrong location, absence of a key symptom), eliminate that condition from further comparison.

Compare symptoms with diseases in the context and identify which ones are consistent with the user’s symptoms.

Then assess based on the match:

If more than 2 diseases match:

Conclude that the information is not sufficient for a confident assessment.

Suggest follow-up questions (marked with a ?) that would help improve diagnostic accuracy.

If only 1 or 2 diseases match:

Select the condition that best fits the symptoms.

Provide the name of the disease, associated symptoms, and treatment (as described in the context).

Responses must remain professional, empathetic, and encourage the user to see a healthcare provider if symptoms worsen or persist.

Let's think step by step:
Translate to thai language.

--------------------------------------------------

Context:
{context}

User's Question:
{input}

"""
prompt = PromptTemplate.from_template(template)
qa_chain = create_stuff_documents_chain(llm, prompt)

def retrival(query):
    results = vectordb.similarity_search(query, k=5)
    top_results_for_rag = []
    for top in results[:5]:
        disease_name = top.metadata.get("disease", "ไม่พบชื่อโรค")
        symptoms = top.page_content
        treatment_steps = next((d["treatment"] for d in doc if d["disease"] == disease_name), [])
        top_results_for_rag.append({
            "disease": disease_name,
            "symptoms": symptoms,
            "treatment": treatment_steps})
    return top_results_for_rag

def llm_respose(query, top_results_for_rag, bool=False):
    context_text = ""
    for item in top_results_for_rag:
        treatment = " / ".join(item["treatment"]) if item["treatment"] else "ไม่พบข้อมูลการรักษา"
        context_text += f"Disease: {item['disease']}\nSymptoms: {item['symptoms']}\nTreatment: {treatment}\n\n"

    context_doc = Document(page_content=context_text)

    start = time.perf_counter()
    response = qa_chain.invoke({
        "input": query,
        "context": [context_doc]
    })
    elapsed = time.perf_counter() - start
    print(f"Typhoon QA chain took {elapsed:.3f} seconds")
    return response, []

st.set_page_config(page_title="MEDICAL AI")
st.title("MEDICAL AI")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

new_user_input = st.text_input("Please type your symptoms.", key="user_input")

if new_user_input:
    st.session_state.chat_history.append(HumanMessage(content=new_user_input))

    full_user_input = ""
    for msg in st.session_state.chat_history:
        if isinstance(msg, HumanMessage):
            full_user_input += msg.content + " "

    with st.spinner(""):
        top_results_for_rag = retrival(full_user_input.strip())
        response, _ = llm_respose(full_user_input.strip(), top_results_for_rag, True)
        for disease in top_results_for_rag:
            st.write(f"- {disease}")
    
    st.session_state.chat_history.append(AIMessage(content=response))

if st.button("Clear chat history"):
    st.session_state.chat_history = []
    st.experimental_rerun()

st.markdown("---")
st.subheader("Chat History")

for msg in st.session_state.chat_history:
    if isinstance(msg, HumanMessage):
        st.markdown(f"🧑‍⚕️: {msg.content}")
    elif isinstance(msg, AIMessage):
        st.markdown(f"🤖: {msg.content}")
