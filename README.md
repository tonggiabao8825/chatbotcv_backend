Huong dan chay du an:


```
Folder app/ se la backend cua du an, viet bang python. 
SUa thong tin o data.json de phu hop voi thong tin cua ban than.
Sua system prompt trong chat_services de cau hinh lai cho phu hop voi van phong cua chatbot.
```

**Cach chay**
Terminal: 
```
cd app 
pip install -r requirements.txt
uvicorn main:app --reload
```

Trong frontend/assets/js/chatbot.js, thay doi    :
         const response = await fetch("{port}/chat", 


neu ko gui duoc req cho server thi sua cau hinh cors trong app/main.py thanh *


**FIle docker dung de compose thi tu hoc di ku**

