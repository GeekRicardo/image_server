base_url="http://localhost:5800"
base_url="http://image.sshug.cn"

echo "Upload Success:"
for i in "$@"; do
    printf "${base_url}/" 
    curl -X POST "$base_url/upload" -H "Html: 0" -H "accept: */*"  -H "Content-Type: multipart/form-data" -H "filepath: $remote_path" -H "PToken: 1fa81717-2bbc-4dca-a00f-887ebe7c2596" -F "file=@$i" 
    echo ""
done
