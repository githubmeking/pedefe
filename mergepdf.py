from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import PyPDF2
import os
import tempfile

TOKEN = '7788432697:AAHgrbNlBuIy3RIcKrAO4YeZSChSAcIPQOc'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Merhaba! PDF dosyalarını birleştirmek için bana gönderin.')

async def merge_pdfs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.document.mime_type != 'application/pdf':
        await update.message.reply_text('Lütfen geçerli bir PDF dosyası gönderin.')
        return

    # Geçici dosya oluştur
    with tempfile.TemporaryDirectory() as tmpdirname:
        file = await update.message.document.get_file()
        file_path = os.path.join(tmpdirname, update.message.document.file_name)
        await file.download_to_drive(file_path)
        
        # Kullanıcının gönderdiği PDF dosyalarını saklamak için user_data kullanıyoruz
        pdf_files = context.user_data.get('pdf_files', [])
        pdf_files.append(file_path)
        context.user_data['pdf_files'] = pdf_files

        await update.message.reply_text(f"{len(pdf_files)}/8 PDF dosyası yüklendi.")

        if len(pdf_files) == 8:
            merger = PyPDF2.PdfMerger()
            for pdf in pdf_files:
                merger.append(pdf)
            merged_path = os.path.join(tmpdirname, "merged.pdf")
            merger.write(merged_path)
            merger.close()

            # Birleştirilmiş PDF'i gönder
            with open(merged_path, "rb") as merged_file:
                await update.message.reply_document(merged_file, filename="merged.pdf")

            # Kullanıcı verisini temizle
            context.user_data['pdf_files'] = []

def main():
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Document.ALL, merge_pdfs))

    application.run_polling()

if __name__ == '__main__':
    main()
