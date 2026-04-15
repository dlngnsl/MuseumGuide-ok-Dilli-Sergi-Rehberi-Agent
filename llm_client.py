import requests
import json

class LLMClient:
    def __init__(self,
                 base_url="http://localhost:1234/v1",
                 model="qwen2.5-0.5b-instruct",
                 temperature=0.3,
                 max_tokens=300):
        """
        LM Studio üzerinde çalışan Qwen modeline bağlanmak için istemci sınıfı.
        """
        self.base_url = base_url
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    def generate_response(self, question, context="", language="tr", system_prompt=None):
        """
        Kullanıcı sorusuna, verilen bağlamı kullanarak yanıt üretir.
        
        :param question: Kullanıcının sorduğu soru
        :param context: RAG sisteminden gelen ilgili metin
        :param language: Yanıtın üretileceği dil (varsayılan: Türkçe)
        :param system_prompt: Özel sistem prompt'u (varsa)
        :return: Model tarafından üretilen yanıt
        """

        # Sistem mesajı: Modelin nasıl davranacağını belirler
        if system_prompt:
            system_content = system_prompt
        else:
            system_content = (
                "Sen bir müze sergi rehberisin. "
                "Ziyaretçilere eserler hakkında doğru, kısa ve anlaşılır bilgiler ver. "
                "Yanıtlarını belirtilen dilde oluştur. "
                "Eğer verilen bağlamda cevap yoksa 'Bu eser hakkında bilgi bulunmamaktadır.' de."
            )

        # Kullanıcı mesajı: RAG bağlamı + soru
        user_prompt = f"""
Bağlam:
{context}

Soru:
{question}

Lütfen yanıtını {language} dilinde ver.
"""

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_content},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }

       

        try:
            response = requests.post(
    f"{self.base_url}/chat/completions",
    json=payload,
    timeout=60
)
            response.raise_for_status()
            result = response.json()

            return result["choices"][0]["message"]["content"].strip()

        except requests.exceptions.RequestException as e:
            return f"LLM bağlantı hatası: {str(e)}"


# Test amaçlı çalıştırma
if __name__ == "__main__":
    llm = LLMClient()
    test_context = (
        "Eser Adı: Antik Vazo\n"
        "Tarih: MÖ 5. yüzyıl\n"
        "Açıklama: Bu vazo, Antik Yunan dönemine ait olup seramik sanatının önemli örneklerindendir."
    )
    question = "Bu eser nedir?"

    answer = llm.generate_response(question, context=test_context)
    print("Model Yanıtı:", answer)