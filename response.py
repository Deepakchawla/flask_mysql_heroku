# dict of response for each type of intent

import datetime

response = {
    "greet": ["hey", "hello", "hi"],
    "fine": ["Feeling great! What can I do for you?"],
    "Good morning": ["Good morning"],
    "Good afternoon": ["Good afternoon"],
"Good evening": ["Good evening"],
"Good night": ["Good night"],
    "goodbye": ["bye", "It was nice talking to you", "see you", "ttyl", "Goodbye, take care", "Your most welcome"],
    "affirm": ["cool", "I know you would like it", "I am glad to hear it", "I am fine, thank you what can I do for you", "I am better now that I am talking to you", "Just searching for answers to life's big (and small) questions, what can I do for you?"],
    "coronovirus" : ["A novel coronavirus is a new coronavirus that has not been previously identified. The virus causing coronavirus disease 2019 (COVID-19), is not the same as the coronaviruses that commonly circulate among humans and cause mild illness, like the common cold."],
    "intro": ["Myself Assistant. Surname Positide. Just open the chat tab, ready to help. I give you information for your request"],
    "spread": ["The new coronavirus appears to spread from person to person among those in close contact. It is spread by respiratory droplets when someone infected with the virus coughs or sneezes. It's unclear exactly how contagious the virus is.", "The new coronavirus appears to spread from person to person among those in close contact. It is spread by respiratory droplets when someone infected with the virus coughs or sneezes. It's unclear exactly how contagious the virus is.People can catch COVID-19 from others who have the virus. The disease can spread from person to person through small droplets from the nose or mouth which are spread when a person with COVID-19 coughs or exhales. These droplets land on objects and surfaces around the person. Other people then catch COVID-19 by touching these objects or surfaces, then touching their eyes, nose or mouth. People can also catch COVID-19 if they breathe in droplets from a person with COVID-19 who coughs out or exhales droplets. This is why it is important to stay more than 1 meter (3 feet) away from a person who is sick.",
               """Coronavirus spreads from an infected person through 👇

♦ Small droplets from the nose or mouth which are spread when a person coughs or sneezes 

♦ Touching an object or surface with these droplets on it and then touching your mouth, nose, or eyes before washing your hands

♦ Close personal contact, such as touching or shaking hand

Please watch the video for more information 👇
ttps://youtu.be/0MgNgcwcKzE""","""According to the World Health Organization, it is not certain how long the virus that causes COVID-19 survives on surfaces, but it seems to behave like other coronaviruses. Studies suggest that coronaviruses (including preliminary information on the COVID-19 virus) may persist on surfaces for a few hours or up to several days. This may vary under different conditions (e.g. type of surface, temperature or humidity of the environment).
If you think a surface may be infected, clean it with a common household disinfectant to kill the virus and protect yourself and others. Clean your hands with an alcohol-based hand rub or wash them with soap and water. Avoid touching your eyes, mouth, or nose."""

               ""],
    "spread air" : ["Studies to date suggest that the virus that causes COVID-19 is mainly transmitted through contact with respiratory droplets rather than through the air. See previous answer on “How does COVID-19 spread?”",

                    ],
"protection": ["""
Keep your immune system healthy by getting plenty of SLEEP, nutrition, stress-relief, and exercise. 

Wash your hands with soap and water or alcohol-based hand sanitizer (contains at least 60% alcohol) if soap and water are not available. Wash your hands frequently, for at least 20 seconds, and certainly after sneezing or before/after touching your face or a sick person.

Cover your mouth and nose with a disposable tissue or your sleeve (not your hands) when coughing or sneezing, if you are ill

Avoid touching your eyes, nose, and mouth.

Avoid contact with others who are sick

Do not travel while sick.
""", """Coronavirus infection can be prevented through the following means 👇

✔ Clean hand with soap and water or alcohol-based hand rub 
https://youtu.be/EJbjyo2xa2o

✔ Cover nose and mouth when coughing & sneezing with a tissue or flexed elbow
https://youtu.be/f2b_hgncFi4

✔ Avoid close contact & maintain 1-meter distance with anyone who is coughing or sneezing
https://youtu.be/mYyNQZ6IdRk

✔ Isolation of persons traveling from affected countries or places for at least 14 days
https://www.mohfw.gov.in/AdditionalTravelAdvisory1homeisolation.pdf

✔ Quarantine if advised
https://www.mohfw.gov.in/Guidelinesforhomequarantine.pdf

"""],

    "vaccine": ["A vaccine for this coronavirus is not available at this time, although a lot of labs are working on it. The seasonal flu vaccine does not prevent the coronavirus, however it does prevent the flu - which is still circulating in our community, and prevention of those infections of which we have a better chance is more important now than ever. CDC recommends that everyone over 6 months of age get the seasonal flu vaccine because it will help protect you for the most common strains of the flu prevalent now.", ""],
    "mask" :["Surgical masks (the paper kind) may help limit transmission of YOUR COLD to others if you are sick; they are not recommended in this country for protecting a healthy person. Any value they do have maybe by stopping people from directly touching their mouth and nose, which is a common way that viruses and germs enter the body. But washing hands and avoiding touching your face work just as well"],
    "info": ["A novel coronavirus is a new coronavirus that has not been previously identified. The virus causing coronavirus disease 2019 (COVID-19), is not the same as the coronaviruses that commonly circulate among humans and cause mild illness, like the common cold."],
"advice": ["""Please watch the videos by Director, AIIMS - Delhi to learn and clear your doubts on Coronavirus 👇

https://youtu.be/JXobDg2Fpn4

https://youtu.be/E8-UoeWewFI

https://youtu.be/5wCZdcAsvE8

https://youtu.be/mYyNQZ6IdRk

https://youtu.be/08ryxbcT3-o"""],
    "know more" : ["https://www.mygov.in/covid-19"],
    "help" : ["""For medical help in India please reach out to the 24/7 Control Room.

📞 Phone: +91-11-23978046
☎ Toll-Free Number: 1075
✉ Email: ncov2019@gov.in
💬 For Whatsapp Text: 9013151515

For queries from a person outside India. Please contact Ministry of External Affairs(MEA), GOI

📞 1800118797
✉ covid19@mea.gov.in

For Visa related queries

📞 01124300666
✉ support.covid19-boi@gov.in""", "I can give you answers of your questions", "Sure, ask me", "Sure, how can I help you?"],

    "sysmptoms": ["""
    Coronaviruses are a large family of viruses, some causes illness in people. Its symptoms in humans are

 🤒 Fever
 😐 Breathing problem
 🤧 Coughing
 😫 Tightness of chest
 👃 Running Nose
 😨 Headache
 🌡 Feeling unwell
 😷 Pneumonia
 💉 Kidney Failure

It can be difficult to identify the disease based on symptoms alone. Check when you should get tested 👇
https://www.mohfw.gov.in/FINAL_14_03_2020_ENg.pdf

You can also view the video on symptoms by Director,AIIMS-Delhi 👇
https://youtu.be/E8-UoeWewFI
    
    """],
    "treatment" : ["A vaccine for this coronavirus is not available at this time, although a lot of labs are working on it. The seasonal flu vaccine does not prevent the coronavirus, however it does prevent the flu - which is still circulating in our community, and prevention of those infections of which we have a better chance is more important now than ever. CDC recommends that everyone over 6 months of age get the seasonal flu vaccine because it will help protect you for the most common strains of the flu prevalent now."],
"difference between": ["""
The first symptoms of COVID-19 and influenza (flu) infections are often very similar. They both cause fever and similar respiratory symptoms, which can then range from mild through to severe disease, and sometimes can be fatal.
Both viruses are also transmitted in the same way, by coughing or sneezing, or by contact with hands, surfaces or objects contaminated with the virus. As a result, the same public health measures, such as hand hygiene (hand washing), good respiratory etiquette (coughing into your elbow or into a tissue and immediately disposing of the tissue) and good household cleaning are important actions to prevent both infections.

The speed of transmission is an important difference between the two viruses. Influenza typically has a shorter incubation period (the time from infection to appearance of symptoms) than COVID-19. This means that influenza can spread faster than COVID-19.

While the range of symptoms for the two viruses is similar, the fraction with severe disease appears to be higher for COVID-19. While most people have mild symptoms, approximately 15% of people have severe infections and 5% require intensive care in a hospital ICU. The proportions of severe and critical COVID-19 infections are higher than for influenza infections
"""],
"most risk": ["""
Based on what we know so far about COVID-19 and what we know about other coronaviruses, those at greatest risk of serious infection are:
people aged 65 years and over
Aboriginal people (as they have higher rates of chronic illness)
people with chronic medical conditions, such as lung disease, heart disease, kidney disease, neurological conditions and diabetes
people with impaired immune systems (such as people who have cancer or HIV, or who take high dose corticosteroids).
People living in group residential settings are at greater risk of being exposed to outbreaks of COVID-19 if a case is diagnosed in a resident or staff member. This includes:

people living in residential aged care facilities and disability group homes
people in detention facilities
students in boarding schools
people on Cruise Ships.
People living in some group residential settings are also more likely to have conditions that make them at greater risk of serious COVID-19 infection.
"""],
"Social distancing": ["""
Social distancing means we reduce the number of close physical and social contacts we have with one another.

When social distancing actions are combined with good personal hygiene measures the spread of a pandemic through the community can be slowed. This helps protect the most vulnerable members of the community and reduces the impact of the pandemic on essential, life-saving health services.

Social distancing is an effective measure, but it is recognised that it cannot be practised in all situations and the aim is to generally reduce potential for transmission.

While practising social distancing, people can travel to work (including public transport). For non-essential activities outside the workplace or attendance at schools, universities and childcare - social distancing includes:

avoiding crowds and mass gatherings where it is difficult to keep the appropriate distance away from others
avoiding small gatherings in enclosed spaces, for example family celebrations
attempting to keep a distance of 1.5 metres between themselves and other people where possible, for example when they are out and about in public place.
avoiding shaking hands, hugging, or kissing other people.
avoiding visiting vulnerable people, such as those in aged care facilities or hospitals, infants, or people with compromised immune systems due to illness or medical treatment.
"""],
    "outdoor": ["No, On 23 March 2020 the Minister made Public Health Order that directs the closure of certain places of social gathering (Places Order), including gyms and other indoor recreation facilities."],
    "Home isolation": ["""
    Yes. If you are sharing your home with others, you should stay in a different room from other people or be separated as much as possible. Wear a surgical mask when you are in the same room as another person, and when seeking medical care. Use a separate bathroom, if available.

Make sure that you do not share a room with people who are at risk of severe disease, such as elderly people and those who have heart, lung or kidney conditions, and diabetes.

Visitors who do not have an essential need to be in the home should not visit while you are isolating
    """, "If you need groceries or medicines (including prescription medicines), ask a family member or friend (who is not in isolation) to deliver them to your home or shop for groceries online. To prevent infecting other people, make sure you wear a mask when receiving a delivery or have the groceries left at your door."],
"name": ["Myself Assistant. Surname Positide. Just open the chat tab, ready to help", "I am your Positide Assistant. I can help you find answers, get things done and have fun"],

"human": ["Yes I am a real robot, but I’m a good one. Let me prove it. How can I help you?", "No I am a robot, but I’m a good one. Let me prove it. How can I help you?"],
    "age" : ["I was launched in 2020, but I am wise beyond my years" ],
    "boss": ["I was made by a team at Positide", "You, most certainly are the boss of me.", "I hope I become a better assistant with every update", "I started out as an idea, then many teams at Positide helped bring me to life."],
    "speak": ["English"],
    "famlity" : ["My team is like my family, lots of people helped me become what I am today"],
    "location": ["I live in the cloud, so I'm here whenever you'd like to chat."],
    "price" : ["Hmm.. I am not sure"],
    "default": ["Sorry I am not trained to answer that yet.", "Oops I didn't understand that sorry"]
}