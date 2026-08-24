$root = 'F:\nilekey\nile-key-project\nile-key2'
$paths = @("$root\.kilo\plans", "$root\.kilo\audits", "$root\PLAN.md", "$root\CURRENT_STATUS.md", "$root\TECH_DEBT.md", "$root\CHANGELOG.md", "$root\README.md")
$allFiles = @()
foreach ($p in $paths) {
    if (Test-Path -LiteralPath $p -PathType Container) {
        $allFiles += Get-ChildItem -LiteralPath $p -Recurse -File | Where-Object { $_.Extension -match '\.(md|txt|json|csv|png)$' } | Select-Object -ExpandProperty FullName
    }
    elseif (Test-Path -LiteralPath $p -PathType Leaf) {
        $allFiles += $p
    }
}
$allFiles = $allFiles | Sort-Object -Unique

$refMap = @{}
foreach ($f in $allFiles) {
    $rel = $f.Replace("$root\", "")
    $name = [System.IO.Path]::GetFileName($f)
    $refs = @()
    foreach ($other in $allFiles) {
        if ($other.FullName -eq $f) { continue }
        $otherRel = $other.Replace("$root\", "")
        $otherName = [System.IO.Path]::GetFileName($other)
        $content = Get-Content $other -Raw -ErrorAction SilentlyContinue
        if ($content -match [regex]::Escape($otherName)) {
            $refs += $otherRel
        }
    }
    # Limit to top 10 refs and filter out self-references
    $refMap[$rel] = ($refs | Select-Object -First 10) -join '; '
}

$refMap.GetEnumerator() | Sort-Object Name | ConvertTo-Json | Out-File -LiteralPath 'F:\nilekey\nile-key-project\nile-key2\governance-refs.json'
Write-Host "Reference map generated for $($refMap.Count) files"
