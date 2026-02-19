param(
    [string]$BranchName = "gateway/test-fixes-draft"
)

Write-Host "Preparing local branch: $BranchName"

git checkout -b $BranchName

Write-Host "You should now edit files under services/gateway according to services/gateway/patches/README.md"
Write-Host "Run tests locally to verify changes before pushing. Example commands:"
Write-Host "  cd services/gateway"
Write-Host "  go test ./... -v 2>&1 | Tee-Object gateway-tests.log"

Write-Host "When ready to push: git add -A ; git commit -m 'test(gateway): draft fixes' ; git push --set-upstream origin $BranchName"
