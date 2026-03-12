Here is the refined README in professional, standard English. I have translated the sections while maintaining the technical structure of your project.

---

# Email Secure+

A web-based application designed to detect phishing emails using Machine Learning and real-time DNS verification.

**Live demo:** [https://emailsecure.streamlit.app](https://emailsecure.streamlit.app)

---

## How It Works

**1. Text Analysis (NLP)**
The model utilizes a TF-IDF and Logistic Regression pipeline to analyze patterns in email body text. It was trained on 150,000 public dataset entries from Kaggle, encompassing both phishing and legitimate emails.

**2. Domain Verification via DNS**
When a sender's email address is provided, the system performs a DNS lookup to check for existing SPF and DMARC records. These results are used to adjust the risk score—domains with full protection receive a score reduction, while those without SPF/DMARC records receive a risk premium.

**3. Final Risk Scoring**
The final score is calculated as: `Model Score × DNS Multiplier`. Results are categorized into three levels:

* **≥ 65%** → Phishing Detected
* **40–64%** → Suspicious Email
* **< 40%** → Safe

---

## 🛠️ Challenges & Debugging

Building this project involved overcoming several technical hurdles that provided valuable insights into software development and system integration:

* **Version Control:** Resolved `non-fast-forward` errors arising from conflicts between manual web uploads and local Git commits. Implemented proper Git branching and synchronization strategies to maintain a clean, professional repository history.
* **Dependency Management:** Diagnosed `ImportError` and `ModuleNotFoundError` issues by isolating the development environment using `.venv` and ensuring the `requirements.txt` file accurately reflected necessary packages, such as `dnspython` and `google-generativeai`.
* **API Rate Limit Handling:** Encountered `429 RESOURCE_EXHAUSTED` errors when querying external APIs. Implemented error handling with `try-except` blocks to provide graceful user feedback and prevent application crashes.
* **Environment Configuration:** Debugged Python interpreter pathing issues within VS Code to ensure consistent application behavior across local virtual environments and production paths.

---

## Dataset

* **Source:** [Kaggle: Phishing Email Dataset](https://www.kaggle.com/datasets/naserabdullahalam/phishing-email-dataset)
* **Size:** 150,000 rows (77,449 phishing, 72,551 legitimate)
* **Features Used:** `text_combined` (email text), `label` (0/1)

---

## Model Pipeline

```
Pipeline:
  TfidfVectorizer(max_features=15000, ngram_range=(1,3), stop_words='english')
  LogisticRegression(C=0.1, class_weight='balanced', max_iter=1000)

```

The model is serialized as `phishing_model.joblib`. The preprocessing logic in `app.py` uses a `clean_text` function identical to the one used during training to ensure data consistency.

---

## Getting Started

```bash
pip install -r requirements.txt
streamlit run app.py

```

Or visit the live application: [https://emailsecure.streamlit.app](https://emailsecure.streamlit.app)

---

## File Structure

```
├── app.py                      # Streamlit application
├── email_phishing_training.ipynb # Training notebook
├── phishing_model.joblib         # Trained model
├── requirements.txt            # Project dependencies
└── README.md

```

---

## Tech Stack

* **Frontend/Backend:** Python, Streamlit
* **Machine Learning:** Scikit-learn (TF-IDF + Logistic Regression)
* **Network Utilities:** dnspython (DNS lookup for SPF/DMARC)
* **Serialization:** Joblib
