# 1. GET запрос
$get_num = Get-Random -Minimum 1 -Maximum 11
Write-Output "1. Отправляем GET с param=$get_num"
$get_response = curl.exe -s "http://localhost:5000/number/?param=$get_num"
$get_data = $get_response | ConvertFrom-Json
Write-Output "Ответ: $($get_data | ConvertTo-Json -Compress)"

# 2. POST запрос
$post_num = Get-Random -Minimum 1 -Maximum 11
Write-Output "`n2. Отправляем POST с jsonParam=$post_num"
$post_response = curl.exe -s -X POST -H "Content-Type: application/json" -d "{\`"jsonParam\`":$post_num}" http://localhost:5000/number/
$post_data = $post_response | ConvertFrom-Json
Write-Output "Ответ: $($post_data | ConvertTo-Json -Compress)"

# 3. DELETE запрос
Write-Output "`n3. Отправляем DELETE"
$delete_response = curl.exe -s -X DELETE http://localhost:5000/number/
$delete_data = $delete_response | ConvertFrom-Json
Write-Output "Ответ: $($delete_data | ConvertTo-Json -Compress)"

# 4. Вычисление результата
Write-Output "`n4. Вычисляем результат:"
$expression = "$($get_data.result) $($post_data.operation) $($post_data.result) $($delete_data.operation) $($delete_data.generated_number)"
$result = [math]::Round((Invoke-Expression $expression))
Write-Output "Выражение: $expression"
Write-Output "Результат: $result"
