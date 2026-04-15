# -*- coding: utf-8 -*-
"""
MÜZEREHBERI - RAG Pipeline
ChromaDB + SentenceTransformers ile vektör tabanlı bilgi getirme
"""

import os
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from sentence_transformers import SentenceTransformer
from langchain.embeddings.base import Embeddings


class SentenceTransformerEmbeddings(Embeddings):
    """SentenceTransformer modelini LangChain ile uyumlu hale getirir."""

    def __init__(self, model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        self.model = SentenceTransformer(model_name)

    def embed_documents(self, texts):
        return self.model.encode(texts, show_progress_bar=False).tolist()

    def embed_query(self, text):
        return self.model.encode([text], show_progress_bar=False)[0].tolist()


class RAGPipeline:
    def __init__(self, data_dir="data", persist_dir="vector_db"):
        self.data_dir = data_dir
        self.persist_dir = persist_dir
        self.embeddings = SentenceTransformerEmbeddings()
        self.exhibits = {}  # eser_id -> eser bilgileri

        # Eser dosyalarını oku ve metadata oluştur
        self._load_exhibit_metadata()

        # Veritabanını yükle veya oluştur
        if os.path.exists(self.persist_dir):
            self.db = Chroma(
                persist_directory=self.persist_dir,
                embedding_function=self.embeddings
            )
            # Boş veritabanı kontrolü — otomatik yeniden indeksleme
            try:
                docs = self.db.get()
                if len(docs.get("documents", [])) == 0:
                    print("⚠️  Veritabanı boş, yeniden indeksleniyor...")
                    self.db = self._create_vector_db()
            except Exception:
                self.db = self._create_vector_db()
        else:
            self.db = self._create_vector_db()

    def _load_exhibit_metadata(self):
        """data/ klasöründeki tüm eser dosyalarını okur ve metadata dictionary oluşturur."""
        for file in sorted(os.listdir(self.data_dir)):
            if file.endswith(".txt"):
                eser_id = file.replace(".txt", "")
                filepath = os.path.join(self.data_dir, file)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read().strip()

                    # Satırları ayrıştır
                    info = {"id": eser_id, "raw": content}
                    for line in content.split("\n"):
                        line = line.strip()
                        if ":" in line:
                            key, val = line.split(":", 1)
                            key = key.strip().lower().replace(" ", "_")
                            info[key] = val.strip()

                    self.exhibits[eser_id] = info
                except Exception as e:
                    print(f"⚠️  {file} okunamadı: {e}")

    def _load_documents(self):
        """data/ klasöründeki tüm .txt dosyalarını LangChain dokümanı olarak yükler."""
        documents = []
        for file in sorted(os.listdir(self.data_dir)):
            if file.endswith(".txt"):
                loader = TextLoader(
                    os.path.join(self.data_dir, file),
                    encoding="utf-8"
                )
                documents.extend(loader.load())
        return documents

    def _create_vector_db(self):
        """Dokümanları vektör veritabanına dönüştürür."""
        documents = self._load_documents()

        if not documents:
            raise ValueError("❌ data/ klasöründe hiç doküman bulunamadı.")

        # Metinleri parçalara ayır
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )
        splits = text_splitter.split_documents(documents)

        print(f"📚 {len(documents)} doküman, {len(splits)} parçaya bölündü.")

        # ChromaDB oluştur
        db = Chroma.from_documents(
            documents=splits,
            embedding=self.embeddings,
            persist_directory=self.persist_dir
        )
        print("✅ Vektör veritabanı başarıyla oluşturuldu.")
        return db

    def retrieve_context(self, query, k=3):
        """Kullanıcı sorusuna en uygun k adet dokümanı getirir."""
        results = self.db.similarity_search(query, k=k)
        context = "\n\n".join([doc.page_content for doc in results])
        return context

    def retrieve_by_exhibit(self, exhibit_id, query, k=2):
        """Belirli bir eser bağlamında soru yanıtlamak için doküman getirir."""
        # Önce eser bilgisini bağlam olarak ekle
        exhibit_info = self.exhibits.get(exhibit_id, {})
        base_context = exhibit_info.get("raw", "")

        # RAG ile ek bağlam getir
        rag_context = self.retrieve_context(query, k=k)

        # İkisini birleştir
        full_context = f"{base_context}\n\n{rag_context}" if rag_context else base_context
        return full_context

    def get_all_exhibits(self):
        """Tüm eser bilgilerini döner."""
        return list(self.exhibits.values())

    def get_exhibit(self, exhibit_id):
        """Belirli bir eserin bilgilerini döner."""
        return self.exhibits.get(exhibit_id)


# Test amaçlı çalıştırma
if __name__ == "__main__":
    rag = RAGPipeline()

    # Veritabanı kontrolü
    try:
        docs = rag.db.get()
        print(f"\n📊 Veritabanında {len(docs['documents'])} doküman var")
    except Exception as e:
        print(f"Veritabanı kontrol hatası: {e}")

    # Eser listesi
    print(f"📋 Toplam {len(rag.exhibits)} eser yüklendi")
    for eid, info in rag.exhibits.items():
        print(f"   - {eid}: {info.get('eser_adı', 'Bilinmiyor')}")

    # Test sorgusu
    question = "Antik vazo hangi döneme aittir?"
    context = rag.retrieve_context(question)
    print(f"\n🔍 Soru: {question}")
    print(f"📄 Bulunan Bağlam:\n{context}")
