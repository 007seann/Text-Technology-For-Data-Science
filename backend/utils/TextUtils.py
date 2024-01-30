import unicodedata
import re
import sentencepiece as spm



class TextUtils:
    def __init__(self):
        self.char_form = "NFD"
        self.index_path = "../database/index/index_base.txt"
        self.spm_vocab_path = "../database/index/spm_vocab.txt"
    
    def unicode_normalise(self, text):
        return unicodedata.normalize(self.char_form, text).encode('ascii', 'ignore').decode('utf-8')
    
    def create_spm_vocab(self):
        with open(self.index_path, "r") as f:
            text = f.read()
        word_list = re.findall(r"([a-zA-Z]+):", text)
        with open(self.spm_vocab_path, "w") as f:
            for word in word_list:
                f.write(word + "\n")
                
    def encode_spm(self, text):
        sp = spm.SentencePieceProcessor()
        sp.Load("../database/index/bpe-model.model")
        return sp.EncodeAsPieces(text)
        
    
    
if __name__ == "__main__":
    t = TextUtils()
    # testing...
    print(t.unicode_normalise("thisâåæçèéê"))
    #t.create_spm_vocab()
    
    #['▁th', 'is', '▁', 'is', '▁a', '▁t', 'est']
    # print(t.encode_spm("this is a test"))
    