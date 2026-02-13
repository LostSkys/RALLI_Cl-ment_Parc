# Script de correction CORS complète
Write-Host "🔧 CORRECTION CORS COMPLÈTE" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan

# Étape 1: Remplacer app.py (sans Flask-CORS)
Write-Host "`n📝 Étape 1/5: Remplacement de app.py..." -ForegroundColor Yellow
Copy-Item app_NO_CORS.py python/app.py -Force
Write-Host "✅ app.py remplacé (sans Flask-CORS)" -ForegroundColor Green

# Étape 2: Remplacer default.conf (nginx)
Write-Host "`n📝 Étape 2/5: Remplacement de default.conf..." -ForegroundColor Yellow
Copy-Item default.conf.FINAL nginx/default.conf -Force
Write-Host "✅ default.conf remplacé" -ForegroundColor Green

# Étape 3: Redémarrer l'API
Write-Host "`n📝 Étape 3/5: Redémarrage de l'API..." -ForegroundColor Yellow
docker compose restart api
Start-Sleep -Seconds 5
Write-Host "✅ API redémarrée" -ForegroundColor Green

# Étape 4: Redémarrer Nginx
Write-Host "`n📝 Étape 4/5: Redémarrage de Nginx..." -ForegroundColor Yellow
docker compose restart nginx
Start-Sleep -Seconds 3
Write-Host "✅ Nginx redémarré" -ForegroundColor Green

# Étape 5: Vérifier
Write-Host "`n📝 Étape 5/5: Vérification..." -ForegroundColor Yellow

# Vérifier l'API
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000/" -TimeoutSec 5
    Write-Host "✅ API répond: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "⚠️  API ne répond pas encore (attendez 10s)" -ForegroundColor Yellow
}

# Vérifier l'état
Write-Host "`n📊 État des services:" -ForegroundColor Cyan
docker compose ps

Write-Host "`n" -NoNewline
Write-Host "=" * 60 -ForegroundColor Green
Write-Host "✅ CORRECTION TERMINÉE" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Green

Write-Host @"

🌐 PROCHAINES ÉTAPES:

1. Ouvrez ou rafraîchissez votre navigateur
2. URL: https://parcattraction/accueil
3. Faites Ctrl+Shift+R pour vider le cache
4. Vérifiez la console (F12) - plus d'erreur CORS!

📋 Si problème persiste:
   - Ouvrez en navigation privée
   - Videz complètement le cache du navigateur
   - Regardez les logs: docker compose logs api
"@

$choice = Read-Host "`nOuvrir le navigateur maintenant? (o/N)"
if ($choice -eq "o" -or $choice -eq "oui") {
    Start-Process "https://parcattraction/accueil"
}

Write-Host "`n🎉 Normalement, tout devrait fonctionner maintenant!" -ForegroundColor Green