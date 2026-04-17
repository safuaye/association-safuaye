D'accord ! Je vous donne le contenu complet. On commence par le plus court.

## 📝 Septième fichier : `backend/server.py` (711 lignes)

**Instructions :**

1. **"Add file" → "Create new file"**

2. Name : `backend/server.py`

3. **CONTENU COMPLET** (copiez TOUT du début à la fin) :
Action: file_editor view /app/backend/server.py
Observation: [Showing lines 1-711 of 711 total] /app/backend/server.py:
1|from fastapi import FastAPI, APIRouter, HTTPException
2|from fastapi.responses import StreamingResponse
3|from dotenv import load_dotenv
4|from starlette.middleware.cors import CORSMiddleware
5|from motor.motor_asyncio import AsyncIOMotorClient
6|import os
7|import logging
8|from pathlib import Path
9|from pydantic import BaseModel, Field, ConfigDict, EmailStr
10|from typing import List, Optional
11|import uuid
12|from datetime import datetime, timezone
13|import io
14|
15|ROOT_DIR = Path(__file__).parent
16|load_dotenv(ROOT_DIR / '.env')
17|
18|# MongoDB connection
19|mongo_url = os.environ['MONGO_URL']
20|client = AsyncIOMotorClient(mongo_url)
21|db = client[os.environ['DB_NAME']]
22|
23|# Create the main app without a prefix
24|app = FastAPI()
25|
26|# Create a router with the /api prefix
27|api_router = APIRouter(prefix="/api")
28|
29|# Define Models
30|class Testimonial(BaseModel):
31|    model_config = ConfigDict(extra="ignore")
32|    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
33|    author_name: str
34|    relationship: str
35|    message: str
36|    language: str = "fr"
37|    approved: bool = False
38|    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
39|
40|class TestimonialCreate(BaseModel):
41|    author_name: str
42|    relationship: str
43|    message: str
44|    language: str = "fr"
45|
46|class ContactMessage(BaseModel):
47|    model_config = ConfigDict(extra="ignore")
48|    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
49|    full_name: str
50|    email: str
51|    phone: Optional[str] = None
52|    country: str
53|    message_type: str
54|    message: str
55|    language: str = "fr"
56|    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
57|
58|class ContactMessageCreate(BaseModel):
59|    full_name: str
60|    email: EmailStr
61|    phone: Optional[str] = None
62|    country: str
63|    message_type: str
64|    message: str
65|    language: str = "fr"
66|
67|class NewsArticle(BaseModel):
68|    model_config = ConfigDict(extra="ignore")
69|    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
70|    title: str
71|    content: str
72|    summary: str
73|    language: str = "fr"
74|    published: bool = True
75|    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
76|
77|class NewsArticleCreate(BaseModel):
78|    title: str
79|    content: str
80|    summary: str
81|    language: str = "fr"
82|
83|class DonationGoal(BaseModel):
84|    model_config = ConfigDict(extra="ignore")
85|    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
86|    target_amount: float = 5000.0
87|    current_amount: float = 0.0
88|    currency: str = "EUR"
89|    description: str = "Aider les anciens joueurs d'Ifodjè"
90|    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
91|
92|class MeetingRegistration(BaseModel):
93|    model_config = ConfigDict(extra="ignore")
94|    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
95|    full_name: str
96|    email: str
97|    role: str
98|    meeting_date: str = "2026-04-18"
99|    confirmed: bool = True
100|    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
101|
102|class MeetingRegistrationCreate(BaseModel):
103|    full_name: str
104|    email: EmailStr
105|    role: str
106|
107|class MeetingMinutes(BaseModel):
108|    model_config = ConfigDict(extra="ignore")
109|    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
110|    meeting_date: str
111|    meeting_time: str
112|    location: str
113|    attendees: List[dict]  # [{"name": "...", "role": "...", "signature": "..."}]
114|    agenda_items: List[str]
115|    decisions: List[dict]  # [{"item": "...", "decision": "...", "votes_for": 0, "votes_against": 0}]
116|    notes: str
117|    created_by: str
118|    status: str = "draft"  # draft, final
119|    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
120|
121|class MeetingMinutesCreate(BaseModel):
122|    meeting_date: str
123|    meeting_time: str
124|    location: str
125|    attendees: List[dict]
126|    agenda_items: List[str]
127|    decisions: List[dict]
128|    notes: str
129|    created_by: str
130|
131|class SignatureRequest(BaseModel):
132|    minutes_id: str
133|    attendee_name: str
134|    signature_data: str  # Base64 encoded signature image
135|
136|# Routes
137|@api_router.get("/")
138|async def root():
139|    return {"message": "SAFUAYE Association API - En mémoire de notre père"}
140|
141|@api_router.get("/health")
142|async def health_check():
143|    return {"status": "healthy", "association": "SAFUAYE"}
144|
145|# Testimonials endpoints
146|@api_router.post("/testimonials", response_model=Testimonial)
147|async def create_testimonial(input: TestimonialCreate):
148|    testimonial_dict = input.model_dump()
149|    testimonial_obj = Testimonial(**testimonial_dict)
150|    doc = testimonial_obj.model_dump()
151|    doc['created_at'] = doc['created_at'].isoformat()
152|    await db.testimonials.insert_one(doc)
153|    return testimonial_obj
154|
155|@api_router.get("/testimonials", response_model=List[Testimonial])
156|async def get_testimonials(language: Optional[str] = None, approved_only: bool = True):
157|    query = {}
158|    if language:
159|        query["language"] = language
160|    if approved_only:
161|        query["approved"] = True
162|    
163|    testimonials = await db.testimonials.find(query, {"_id": 0}).to_list(100)
164|    for t in testimonials:
165|        if isinstance(t['created_at'], str):
166|            t['created_at'] = datetime.fromisoformat(t['created_at'])
167|    return testimonials
168|
169|@api_router.put("/testimonials/{testimonial_id}/approve")
170|async def approve_testimonial(testimonial_id: str):
171|    result = await db.testimonials.update_one(
172|        {"id": testimonial_id},
173|        {"$set": {"approved": True}}
174|    )
175|    if result.modified_count == 0:
176|        raise HTTPException(status_code=404, detail="Testimonial not found")
177|    return {"message": "Testimonial approved"}
178|
179|@api_router.delete("/testimonials/{testimonial_id}")
180|async def delete_testimonial(testimonial_id: str):
181|    result = await db.testimonials.delete_one({"id": testimonial_id})
182|    if result.deleted_count == 0:
183|        raise HTTPException(status_code=404, detail="Testimonial not found")
184|    return {"message": "Testimonial deleted"}
185|
186|# Contact/Membership endpoints
187|@api_router.post("/contact", response_model=ContactMessage)
188|async def create_contact(input: ContactMessageCreate):
189|    contact_dict = input.model_dump()
190|    contact_obj = ContactMessage(**contact_dict)
191|    doc = contact_obj.model_dump()
192|    doc['created_at'] = doc['created_at'].isoformat()
193|    await db.contacts.insert_one(doc)
194|    return contact_obj
195|
196|@api_router.get("/contacts", response_model=List[ContactMessage])
197|async def get_contacts():
198|    contacts = await db.contacts.find({}, {"_id": 0}).to_list(100)
199|    for c in contacts:
200|        if isinstance(c['created_at'], str):
201|            c['created_at'] = datetime.fromisoformat(c['created_at'])
202|    return contacts
203|
204|# News/Actualités endpoints
205|@api_router.post("/news", response_model=NewsArticle)
206|async def create_news(input: NewsArticleCreate):
207|    news_dict = input.model_dump()
208|    news_obj = NewsArticle(**news_dict)
209|    doc = news_obj.model_dump()
210|    doc['created_at'] = doc['created_at'].isoformat()
211|    await db.news.insert_one(doc)
212|    return news_obj
213|
214|@api_router.get("/news", response_model=List[NewsArticle])
215|async def get_news(language: Optional[str] = None, published_only: bool = True):
216|    query = {}
217|    if language:
218|        query["language"] = language
219|    if published_only:
220|        query["published"] = True
221|    
222|    news = await db.news.find(query, {"_id": 0}).sort("created_at", -1).to_list(50)
223|    for n in news:
224|        if isinstance(n['created_at'], str):
225|            n['created_at'] = datetime.fromisoformat(n['created_at'])
226|    return news
227|
228|@api_router.get("/news/{news_id}", response_model=NewsArticle)
229|async def get_news_by_id(news_id: str):
230|    news = await db.news.find_one({"id": news_id}, {"_id": 0})
231|    if not news:
232|        raise HTTPException(status_code=404, detail="News not found")
233|    if isinstance(news['created_at'], str):
234|        news['created_at'] = datetime.fromisoformat(news['created_at'])
235|    return news
236|
237|@api_router.put("/news/{news_id}")
238|async def update_news(news_id: str, input: NewsArticleCreate):
239|    result = await db.news.update_one(
240|        {"id": news_id},
241|        {"$set": input.model_dump()}
242|    )
243|    if result.modified_count == 0:
244|        raise HTTPException(status_code=404, detail="News not found")
245|    return {"message": "News updated"}
246|
247|@api_router.put("/news/{news_id}/publish")
248|async def toggle_news_publish(news_id: str, published: bool):
249|    result = await db.news.update_one(
250|        {"id": news_id},
251|        {"$set": {"published": published}}
252|    )
253|    if result.modified_count == 0:
254|        raise HTTPException(status_code=404, detail="News not found")
255|    return {"message": f"News {'published' if published else 'unpublished'}"}
256|
257|@api_router.delete("/news/{news_id}")
258|async def delete_news(news_id: str):
259|    result = await db.news.delete_one({"id": news_id})
260|    if result.deleted_count == 0:
261|        raise HTTPException(status_code=404, detail="News not found")
262|    return {"message": "News deleted"}
263|
264|# Donation Goal endpoints
265|@api_router.get("/donation-goal")
266|async def get_donation_goal():
267|    goal = await db.donation_goals.find_one({}, {"_id": 0})
268|    if not goal:
269|        # Create default goal
270|        default_goal = DonationGoal()
271|        doc = default_goal.model_dump()
272|        doc['updated_at'] = doc['updated_at'].isoformat()
273|        await db.donation_goals.insert_one(doc)
274|        return default_goal.model_dump()
275|    if isinstance(goal.get('updated_at'), str):
276|        goal['updated_at'] = datetime.fromisoformat(goal['updated_at'])
277|    return goal
278|
279|@api_router.put("/donation-goal")
280|async def update_donation_goal(target_amount: Optional[float] = None, current_amount: Optional[float] = None, description: Optional[str] = None):
281|    update_data = {"updated_at": datetime.now(timezone.utc).isoformat()}
282|    if target_amount is not None:
283|        update_data["target_amount"] = target_amount
284|    if current_amount is not None:
285|        update_data["current_amount"] = current_amount
286|    if description is not None:
287|        update_data["description"] = description
288|    
289|    result = await db.donation_goals.update_one({}, {"$set": update_data})
290|    if result.matched_count == 0:
291|        # Create if doesn't exist
292|        goal = DonationGoal(
293|            target_amount=target_amount or 5000.0,
294|            current_amount=current_amount or 0.0,
295|            description=description or "Aider les anciens joueurs d'Ifodjè"
296|        )
297|        doc = goal.model_dump()
298|        doc['updated_at'] = doc['updated_at'].isoformat()
299|        await db.donation_goals.insert_one(doc)
300|    return {"message": "Donation goal updated"}
301|
302|# Donation status endpoint
303|@api_router.get("/donation-status")
304|async def get_donation_status():
305|    """Check if donations are enabled (Stripe configured)"""
306|    stripe_key = os.environ.get('STRIPE_SECRET_KEY', '')
307|    return {
308|        "enabled": bool(stripe_key and stripe_key.startswith('sk_')),
309|        "message": "Donations coming soon" if not stripe_key else "Donations enabled"
310|    }
311|
312|# Meeting Registration endpoints
313|@api_router.post("/meeting/register", response_model=MeetingRegistration)
314|async def register_for_meeting(input: MeetingRegistrationCreate):
315|    registration_dict = input.model_dump()
316|    registration_obj = MeetingRegistration(**registration_dict)
317|    doc = registration_obj.model_dump()
318|    doc['created_at'] = doc['created_at'].isoformat()
319|    await db.meeting_registrations.insert_one(doc)
320|    return registration_obj
321|
322|@api_router.get("/meeting/registrations", response_model=List[MeetingRegistration])
323|async def get_meeting_registrations():
324|    registrations = await db.meeting_registrations.find({}, {"_id": 0}).to_list(100)
325|    for r in registrations:
326|        if isinstance(r['created_at'], str):
327|            r['created_at'] = datetime.fromisoformat(r['created_at'])
328|    return registrations
329|
330|@api_router.get("/meeting/info")
331|async def get_meeting_info():
332|    return {
333|        "date": "2026-04-18",
334|        "time": "11:00-13:00",
335|        "timezone": "Europe/London",
336|        "format": "Online",
337|        "meeting_link": "https://meet.google.com/safuaye-uk-registration",
338|        "objective": "Complete UK CIO Registration",
339|        "language": "French",
340|        "agenda": [
341|            "Ouverture de la séance et appel des présents",
342|            "Adoption de la Constitution (CIO)",
343|            "Nomination officielle des Trustees",
344|            "Définition des objectifs caritatifs",
345|            "Vote sur les résolutions",
346|            "Signature du procès-verbal",
347|            "Clôture"
348|        ]
349|    }
350|
351|# Helper functions for email templates
352|def get_meeting_details_section():
353|    return """📅 DÉTAILS DE LA RÉUNION:
354|━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
355|Date : Dimanche 18 Avril 2026
356|Heure : 11h00 - 13h00 (Heure de Londres / GMT+1)
357|Format : Réunion en ligne
358|Lien de visioconférence : https://meet.google.com/safuaye-uk-registration"""
359|
360|def get_meeting_agenda_section():
361|    return """📋 ORDRE DU JOUR:
362|━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
363|1. Ouverture de la séance et appel des présents
364|2. Adoption de la Constitution (CIO)
365|3. Nomination officielle des Trustees
366|4. Définition des objectifs caritatifs
367|5. Vote sur les résolutions
368|6. Signature du procès-verbal
369|7. Clôture"""
370|
371|def get_meeting_footer():
372|    return """Cordialement,
373|L'équipe SAFUAYE
374|UK • Italie • Suisse • Togo
375|contact@safuaye.org
376|+44 7398 308 310
377|safuaye.org"""
378|
379|def format_participants_list(registrations):
380|    if not registrations:
381|        return "Aucun participant inscrit"
382|    return "\n".join([f"• {r.get('full_name', 'N/A')} - {r.get('role', 'N/A')}" for r in registrations])
383|
384|# Email template endpoint
385|@api_router.get("/meeting/email-template")
386|async def get_meeting_email_template():
387|    registrations = await db.meeting_registrations.find({}, {"_id": 0}).to_list(100)
388|    
389|    email_subject = "SAFUAYE - Convocation Assemblée Constitutive - 18 Avril 2026"
390|    
391|    email_body = f"""Cher(e) membre de SAFUAYE,
392|
393|Nous avons le plaisir de vous confirmer votre inscription à l'Assemblée Constitutive de l'association SAFUAYE.
394|
395|{get_meeting_details_section()}
396|
397|🎯 OBJECTIF:
398|Finaliser l'enregistrement de l'association SAFUAYE comme Charitable Incorporated Organisation (CIO) au Royaume-Uni.
399|
400|{get_meeting_agenda_section()}
401|
402|📄 DOCUMENTS À CONSULTER:
403|Vous pouvez consulter les documents officiels sur notre site : safuaye.org/?admin=safuaye2024
404|
405|⚠️ IMPORTANT:
406|- Merci de vous connecter 5 minutes avant le début
407|- Préparez vos questions éventuelles
408|- Un procès-verbal sera établi et signé électroniquement
409|
410|💚 PARTICIPANTS INSCRITS ({len(registrations)}):
411|━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
412|{format_participants_list(registrations)}
413|
414|En cas d'empêchement, merci de nous prévenir au plus vite.
415|
416|{get_meeting_footer()}
417|"""
418|    
419|    return {
420|        "subject": email_subject,
421|        "body": email_body,
422|        "recipients": [r.get('email') for r in registrations],
423|        "count": len(registrations)
424|    }
425|
426|# WhatsApp message template endpoint
427|@api_router.get("/meeting/whatsapp-template")
428|async def get_meeting_whatsapp_template():
429|    registrations = await db.meeting_registrations.find({}, {"_id": 0}).to_list(100)
430|    
431|    whatsapp_message = f"""🟢 *SAFUAYE - Convocation Officielle*
432|━━━━━━━━━━━━━━━━━━━━━━━━
433|
434|📅 *Date* : Dimanche 18 Avril 2026
435|🕐 *Heure* : 11h00 - 13h00 (Heure de Londres)
436|📱 *Format* : Appel vidéo WhatsApp
437|
438|👥 *Participants - 3 Trustees* :
439|{chr(10).join([f"{i+1}. {r.get('full_name', 'N/A')} - {r.get('role', 'N/A')}" for i, r in enumerate(registrations[:3])])}
440|
441|🎯 *Objectif* :
442|Assemblée Constitutive pour enregistrement CIO au Royaume-Uni
443|
444|📋 *Ordre du jour* :
445|1️⃣ Ouverture et appel
446|2️⃣ Adoption Constitution CIO
447|3️⃣ Nomination Trustees
448|4️⃣ Objectifs caritatifs
449|5️⃣ Vote résolutions
450|6️⃣ Signatures PV
451|7️⃣ Clôture
452|
453|📞 *Instructions réunion* :
454|Le Président lance l'appel vidéo WhatsApp à 11h00 et ajoute les 2 autres trustees au groupe.
455|
456|📄 *Documents* :
457|safuaye.org/?admin=safuaye2024
458|
459|⚠️ *Important* :
460|Document officiel pour Charity Commission UK
461|Procès-verbal sera signé après la réunion
462|
463|💚 *Merci de confirmer votre présence*
464|
465|━━━━━━━━━━━━━━━━━━━━━━━━
466|SAFUAYE Association
467|UK • Italie • Suisse • Togo
468|+44 7398 308 310
469|"""
470|    
471|    return {
472|        "message": whatsapp_message,
473|        "recipients": [r.get('full_name') for r in registrations[:3]],
474|        "phone_numbers": [r.get('email') for r in registrations[:3]],  # Could be replaced with actual phone numbers
475|        "count": min(len(registrations), 3)
476|    }
477|
478|# Meeting Minutes endpoints
479|@api_router.post("/meeting/minutes", response_model=MeetingMinutes)
480|async def create_meeting_minutes(input: MeetingMinutesCreate):
481|    minutes_dict = input.model_dump()
482|    minutes_obj = MeetingMinutes(**minutes_dict)
483|    doc = minutes_obj.model_dump()
484|    doc['created_at'] = doc['created_at'].isoformat()
485|    await db.meeting_minutes.insert_one(doc)
486|    return minutes_obj
487|
488|@api_router.get("/meeting/minutes", response_model=List[MeetingMinutes])
489|async def get_all_meeting_minutes():
490|    minutes = await db.meeting_minutes.find({}, {"_id": 0}).to_list(100)
491|    for m in minutes:
492|        if isinstance(m['created_at'], str):
493|            m['created_at'] = datetime.fromisoformat(m['created_at'])
494|    return minutes
495|
496|@api_router.get("/meeting/minutes/{minutes_id}")
497|async def get_meeting_minutes_by_id(minutes_id: str):
498|    minutes = await db.meeting_minutes.find_one({"id": minutes_id}, {"_id": 0})
499|    if not minutes:
500|        raise HTTPException(status_code=404, detail="Minutes not found")
501|    if isinstance(minutes['created_at'], str):
502|        minutes['created_at'] = datetime.fromisoformat(minutes['created_at'])
503|    return minutes
504|
505|@api_router.post("/meeting/minutes/{minutes_id}/sign")
506|async def sign_meeting_minutes(minutes_id: str, signature: SignatureRequest):
507|    minutes = await db.meeting_minutes.find_one({"id": minutes_id}, {"_id": 0})
508|    if not minutes:
509|        raise HTTPException(status_code=404, detail="Minutes not found")
510|    
511|    # Update attendee with signature
512|    attendees = minutes.get('attendees', [])
513|    for attendee in attendees:
514|        if attendee.get('name') == signature.attendee_name:
515|            attendee['signature'] = signature.signature_data
516|            attendee['signed_at'] = datetime.now(timezone.utc).isoformat()
517|            break
518|    
519|    await db.meeting_minutes.update_one(
520|        {"id": minutes_id},
521|        {"$set": {"attendees": attendees}}
522|    )
523|    
524|    return {"message": "Signature added successfully"}
525|
526|@api_router.post("/meeting/minutes/{minutes_id}/finalize")
527|async def finalize_meeting_minutes(minutes_id: str):
528|    result = await db.meeting_minutes.update_one(
529|        {"id": minutes_id},
530|        {"$set": {"status": "final"}}
531|    )
532|    if result.modified_count == 0:
533|        raise HTTPException(status_code=404, detail="Minutes not found")
534|    return {"message": "Minutes finalized"}
535|
536|# Association info endpoint
537|@api_router.get("/association-info")
538|async def get_association_info():
539|    return {
540|        "name": "SAFUAYE",
541|        "full_name": "SAFUAYE - Association en Hommage à Simon-Joseph Afantchédé APEDO",
542|        "registered_address": "26b Langley Park Road, SM2 5EN Sutton, United Kingdom",
543|        "trustees": [
544|            {"name": "Kokou Ognakotan Apedo", "role": "Chair", "country": "United Kingdom"},
545|            {"name": "Yao Blaise Apedo", "role": "Trustee", "country": "Switzerland"},
546|            {"name": "Ablavi Apedo", "role": "Trustee", "country": "Togo"}
547|        ],
548|        "mission": {
549|            "fr": "Perpétuer l'héritage de générosité de Simon-Joseph Afantchédé APEDO en soutenant les anciens joueurs de football, leurs familles et les personnes démunies d'Atakpamé.",
550|            "en": "To perpetuate the legacy of generosity of Simon-Joseph Afantchédé APEDO by supporting former football players, their families, and underprivileged people in Atakpamé.",
551|            "it": "Perpetuare l'eredità di generosità di Simon-Joseph Afantchédé APEDO sostenendo gli ex calciatori, le loro famiglie e le persone bisognose di Atakpamé."
552|        },
553|        "values": ["Générosité", "Sport", "Communauté", "Entraide", "Mémoire"],
554|        "operations": {
555|            "uk": "Administrative headquarters in the United Kingdom",
556|            "italy": "European coordination in Italy", 
557|            "switzerland": "European coordination in Switzerland",
558|            "togo": "Field operations in Atakpamé, Togo"
559|        }
560|    }
561|
562|# Helper functions for legal guidance
563|def get_uk_legal_steps():
564|    return [
565|        {
566|            "step": 1,
567|            "title": "Choisir le type de structure",
568|            "description": "Pour une association caritative, vous pouvez opter pour un 'Charitable Incorporated Organisation (CIO)' ou une 'Unincorporated Association'. Le CIO offre une personnalité juridique distincte."
569|        },
570|        {
571|            "step": 2,
572|            "title": "Rédiger les statuts (Constitution)",
573|            "description": "Définir les objectifs caritatifs, les règles de gouvernance, les conditions d'adhésion et les procédures de prise de décision."
574|        },
575|        {
576|            "step": 3,
577|            "title": "Enregistrer auprès de la Charity Commission",
578|            "description": "Si vos revenus annuels dépassent £5,000, l'enregistrement est obligatoire. Soumettez votre constitution et les détails des trustees."
579|        },
580|        {
581|            "step": 4,
582|            "title": "Ouvrir un compte bancaire",
583|            "description": "Un compte bancaire dédié est essentiel pour gérer les fonds de l'association de manière transparente."
584|        },
585|        {
586|            "step": 5,
587|            "title": "Mettre en place la gouvernance",
588|            "description": "Nommer au moins 3 trustees, établir un conseil d'administration et documenter toutes les décisions."
589|        }
590|    ]
591|
592|def get_togo_legal_steps():
593|    return [
594|        {
595|            "step": 1,
596|            "title": "Rédiger les statuts",
597|            "description": "Les statuts doivent inclure le nom, le siège social (Atakpamé), l'objet social, les conditions d'adhésion et les organes de direction."
598|        },
599|        {
600|            "step": 2,
601|            "title": "Tenir l'Assemblée Générale Constitutive",
602|            "description": "Réunir les membres fondateurs, adopter les statuts, élire le bureau exécutif et rédiger le procès-verbal."
603|        },
604|        {
605|            "step": 3,
606|            "title": "Déclarer à la Préfecture",
607|            "description": "Déposer une demande de récépissé de déclaration auprès de la préfecture d'Atakpamé avec les statuts, le PV de l'AG et la liste des dirigeants."
608|        },
609|        {
610|            "step": 4,
611|            "title": "Obtenir le récépissé",
612|            "description": "Après vérification, la préfecture délivre un récépissé qui donne une existence légale à l'association."
613|        },
614|        {
615|            "step": 5,
616|            "title": "Publication au Journal Officiel (optionnel)",
617|            "description": "Pour une reconnaissance d'utilité publique, la publication au Journal Officiel peut être requise."
618|        }
619|    ]
620|
621|def get_required_documents():
622|    return {
623|        "common": [
624|            "Statuts de l'association",
625|            "Règlement intérieur",
626|            "Procès-verbal de l'Assemblée Générale Constitutive",
627|            "Liste des membres fondateurs",
628|            "Liste des membres du bureau",
629|            "Pièces d'identité des dirigeants"
630|        ],
631|        "specific_uk": [
632|            "Constitution (modèle CIO disponible)",
633|            "Trustee declaration forms",
634|            "Charity Commission application"
635|        ],
636|        "specific_togo": [
637|            "Demande adressée au Préfet",
638|            "Timbres fiscaux",
639|            "Casier judiciaire des dirigeants (parfois requis)"
640|        ]
641|    }
642|
643|# Legal guidance endpoint
644|@api_router.get("/legal-guidance")
645|async def get_legal_guidance():
646|    return {
647|        "uk": {
648|            "title": "Créer une Association au Royaume-Uni",
649|            "steps": get_uk_legal_steps()
650|        },
651|        "togo": {
652|            "title": "Créer une Association au Togo",
653|            "steps": get_togo_legal_steps()
654|        },
655|        "documents_needed": get_required_documents()
656|    }
657|
658|# Seed initial news articles
659|@api_router.post("/seed-news")
660|async def seed_news():
661|    """Seed initial news articles"""
662|    existing = await db.news.count_documents({})
663|    if existing > 0:
664|        return {"message": "News already seeded"}
665|    
666|    articles = [
667|        {
668|            "id": str(uuid.uuid4()),
669|            "title": "Lancement de l'Association SAFUAYE",
670|            "summary": "L'association SAFUAYE est officiellement lancée pour perpétuer l'héritage de Simon-Joseph Afantchédé APEDO.",
671|            "content": "Nous sommes fiers d'annoncer le lancement officiel de l'association SAFUAYE. Notre mission est de perpétuer l'héritage de générosité de notre père, Simon-Joseph Afantchédé APEDO, dit 'Safuaye', en soutenant les anciens joueurs de football, leurs familles et les personnes démunies d'Atakpamé au Togo.",
672|            "language": "fr",
673|            "published": True,
674|            "created_at": datetime.now(timezone.utc).isoformat()
675|        },
676|        {
677|            "id": str(uuid.uuid4()),
678|            "title": "Identification des premiers bénéficiaires",
679|            "summary": "Six anciens joueurs d'Ifodjè ont été identifiés comme premiers bénéficiaires de l'association.",
680|            "content": "Grâce à notre travail sur le terrain à Atakpamé, nous avons identifié six anciens joueurs de l'équipe Ifodjè qui ont besoin de notre soutien. Ces anciens joueurs, aujourd'hui âgés de 58 à 70 ans, font face à des difficultés financières et de santé. Notre objectif est de leur apporter une aide concrète.",
681|            "language": "fr",
682|            "published": True,
683|            "created_at": datetime.now(timezone.utc).isoformat()
684|        }
685|    ]
686|    
687|    await db.news.insert_many(articles)
688|    return {"message": "News seeded successfully"}
689|
690|# Include the router in the main app
691|app.include_router(api_router)
692|
693|app.add_middleware(
694|    CORSMiddleware,
695|    allow_credentials=True,
696|    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
697|    allow_methods=["*"],
698|    allow_headers=["*"],
699|)
700|
701|# Configure logging
702|logging.basicConfig(
703|    level=logging.INFO,
704|    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
705|)
706|logger = logging.getLogger(__name__)
707|
708|@app.on_event("shutdown")
709|async def shutdown_db_client():
710|    client.close()
711|
[End of file]
