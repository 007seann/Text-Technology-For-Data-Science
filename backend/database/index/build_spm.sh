models=('bpe') #'unigram' 'char' 'word'

echo "$PWD"

DEFAULT_VOCAB_SIZE=200

for i in  "${models[@]}"; do
    echo "------------"
    echo "$i"
    echo -n "Proceed?:"
    spm_train --input="../database/index/spm_vocab.txt" --model_prefix="$i-model" --vocab_size=200 --character_coverage=1.0 --model_type="$i"
    read -r ans
done