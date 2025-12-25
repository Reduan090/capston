"""
Database Seed Script
Populates database with demo data for testing and development.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.auth import get_auth_manager
from utils.database import add_reference
from config import logger

def seed_demo_users():
    """Create demo user accounts."""
    print("\n📝 Creating demo users...")
    
    auth_manager = get_auth_manager()
    
    users = [
        ("demo", "demo@research.bot", "Demo123456"),
        ("researcher", "researcher@research.bot", "Research123"),
        ("student", "student@research.bot", "Student123"),
    ]
    
    created = 0
    for username, email, password in users:
        success, message = auth_manager.register_user(username, email, password)
        if success:
            print(f"  ✅ Created user: {username}")
            created += 1
        else:
            if "already exists" in message.lower():
                print(f"  ⏭️  User {username} already exists")
            else:
                print(f"  ❌ Failed to create {username}: {message}")
    
    print(f"\n✅ Created {created} new user(s)")


def seed_demo_references():
    """Add demo research references."""
    print("\n📚 Adding demo references...")
    
    references = [
        {
            "title": "Attention Is All You Need",
            "authors": "Vaswani, A., Shazeer, N., Parmar, N., et al.",
            "year": "2017",
            "doi": "10.48550/arXiv.1706.03762",
            "bibtex": "@inproceedings{vaswani2017attention, title={Attention is all you need}, author={Vaswani, Ashish and Shazeer, Noam and Parmar, Niki and Uszkoreit, Jakob and Jones, Llion and Gomez, Aidan N and Kaiser, {\L}ukasz and Polosukhin, Illia}, booktitle={Advances in neural information processing systems}, pages={5998--6008}, year={2017}}"
        },
        {
            "title": "BERT: Pre-training of Deep Bidirectional Transformers",
            "authors": "Devlin, J., Chang, M.W., Lee, K., Toutanova, K.",
            "year": "2018",
            "doi": "10.48550/arXiv.1810.04805",
            "bibtex": "@article{devlin2018bert, title={BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding}, author={Devlin, Jacob and Chang, Ming-Wei and Lee, Kenton and Toutanova, Kristina}, journal={arXiv preprint arXiv:1810.04805}, year={2018}}"
        },
        {
            "title": "Language Models are Few-Shot Learners",
            "authors": "Brown, T.B., Mann, B., Ryder, N., et al.",
            "year": "2020",
            "doi": "10.48550/arXiv.2005.14165",
            "bibtex": "@article{brown2020language, title={Language models are few-shot learners}, author={Brown, Tom and Mann, Benjamin and Ryder, Nick and Subbiah, Melanie and Kaplan, Jared D and Dhariwal, Prafulla and Neelakantan, Arvind and Shyam, Pranav and Sastry, Girish and Askell, Amanda and others}, journal={Advances in neural information processing systems}, volume={33}, pages={1877--1901}, year={2020}}"
        },
        {
            "title": "Deep Learning",
            "authors": "Goodfellow, I., Bengio, Y., Courville, A.",
            "year": "2016",
            "doi": "",
            "bibtex": "@book{goodfellow2016deep, title={Deep learning}, author={Goodfellow, Ian and Bengio, Yoshua and Courville, Aaron}, year={2016}, publisher={MIT press}}"
        },
        {
            "title": "ImageNet Classification with Deep Convolutional Neural Networks",
            "authors": "Krizhevsky, A., Sutskever, I., Hinton, G.E.",
            "year": "2012",
            "doi": "10.1145/3065386",
            "bibtex": "@article{krizhevsky2012imagenet, title={Imagenet classification with deep convolutional neural networks}, author={Krizhevsky, Alex and Sutskever, Ilya and Hinton, Geoffrey E}, journal={Communications of the ACM}, volume={60}, number={6}, pages={84--90}, year={2017}, publisher={AcM New York, NY, USA}}"
        }
    ]
    
    added = 0
    for ref in references:
        try:
            add_reference(
                title=ref["title"],
                authors=ref["authors"],
                year=ref["year"],
                doi=ref["doi"],
                bibtex=ref["bibtex"]
            )
            print(f"  ✅ Added: {ref['title'][:50]}...")
            added += 1
        except Exception as e:
            print(f"  ⏭️  Skipping (may exist): {ref['title'][:50]}...")
            logger.debug(f"Reference add error: {e}")
    
    print(f"\n✅ Added {added} reference(s)")


def create_sample_uploads():
    """Create sample document structure."""
    print("\n📁 Creating sample upload structure...")
    
    from config import UPLOAD_DIR, VECTOR_DB_DIR, BASE_DIR
    
    # Create user directories for demo users
    demo_dirs = [
        UPLOAD_DIR / "user_1",
        UPLOAD_DIR / "user_2", 
        UPLOAD_DIR / "user_3",
        VECTOR_DB_DIR / "user_1",
        VECTOR_DB_DIR / "user_2",
        VECTOR_DB_DIR / "user_3",
        BASE_DIR / "exports" / "user_1",
        BASE_DIR / "exports" / "user_2",
        BASE_DIR / "exports" / "user_3",
    ]
    
    created = 0
    for dir_path in demo_dirs:
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            created += 1
    
    print(f"  ✅ Created {created} user directories")
    
    # Create sample text file
    sample_text = """Sample Research Document

This is a sample document for testing the Research Bot application.

Introduction
============
This document demonstrates the document upload and processing capabilities.

Methodology
===========
The system uses vector embeddings and FAISS for semantic search.

Results
=======
The implementation successfully processes PDF, DOCX, TXT, and LaTeX files.

Conclusion
==========
The Research Bot provides powerful AI-assisted research capabilities.
"""
    
    sample_file = UPLOAD_DIR / "user_1" / "sample_research.txt"
    if not sample_file.exists():
        with open(sample_file, "w", encoding="utf-8") as f:
            f.write(sample_text)
        print(f"  ✅ Created sample document: sample_research.txt")


def seed_all():
    """Run all seed functions."""
    print("\n" + "="*60)
    print("DATABASE SEEDING - Demo Data")
    print("="*60)
    
    seed_demo_users()
    seed_demo_references()
    create_sample_uploads()
    
    print("\n" + "="*60)
    print("✅ SEEDING COMPLETE")
    print("="*60)
    print("\n📝 Demo Credentials:")
    print("  Username: demo     | Password: Demo123456")
    print("  Username: researcher | Password: Research123")
    print("  Username: student  | Password: Student123")
    print("\n🚀 Run: streamlit run app.py")
    print("="*60 + "\n")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Seed database with demo data")
    parser.add_argument("--users", action="store_true", help="Seed users only")
    parser.add_argument("--references", action="store_true", help="Seed references only")
    parser.add_argument("--files", action="store_true", help="Create sample files only")
    
    args = parser.parse_args()
    
    if args.users:
        seed_demo_users()
    elif args.references:
        seed_demo_references()
    elif args.files:
        create_sample_uploads()
    else:
        # Run all if no specific flag
        seed_all()
