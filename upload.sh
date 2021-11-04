base_url="http://image.sshug.cn"
base_url="http://localhost:5800"

echo "Upload Success:"
for i in "$@"; do
    printf "${base_url}/" 
    curl -X POST "$base_url/upload" -H "accept: */*"  -H "Content-Type: multipart/form-data" -H "filepath: $remote_path" -F "file=@$i"
    echo ""
done