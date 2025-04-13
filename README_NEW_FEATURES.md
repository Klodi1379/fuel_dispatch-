# Veçoritë e Reja të Sistemit të Menaxhimit të Karburantit

Ky dokument përshkruan veçoritë e reja të shtuara në sistemin e menaxhimit të karburantit dhe si t'i përdorni ato.

## 1. Gjurmimi i Automjeteve në Kohë Reale

Sistemi tani ofron gjurmim të automjeteve në kohë reale me këto funksionalitete:

- **Harta Interaktive**: Shfaq vendndodhjen e automjeteve në një hartë interaktive
- **Përditësime në Kohë Reale**: Merr përditësime të vendndodhjes së automjeteve përmes WebSockets
- **Historiku i Lëvizjeve**: Shfaq historikun e lëvizjeve të një automjeti për një periudhë të caktuar

### Si ta përdorni:

1. Shkoni te **Gjurmimi > Gjurmimi në Kohë Reale** në menunë kryesore
2. Në hartë do të shfaqen të gjitha automjetet aktive
3. Klikoni mbi një automjet në listë për të fokusuar hartën tek ai
4. Për të parë historikun e lëvizjeve, përdorni API-në në `/tracking/api/locations/{vehicle_id}/history/`

### Për zhvilluesit:

Për të dërguar përditësime të vendndodhjes, përdorni WebSocket në `/ws/tracking/` me këtë format:

```json
{
  "type": "vehicle_location",
  "vehicle_id": 1,
  "latitude": 41.3275,
  "longitude": 19.8187
}
```

## 2. Optimizimi i Rrugëve

Sistemi tani mund të optimizojë rrugët për dërgesat e karburantit:

- **Llogaritja e Rrugës Optimale**: Përdor OpenStreetMap për të gjetur rrugën më të shkurtër
- **Vlerësimi i Kohës dhe Distancës**: Llogarit distancën dhe kohën e parashikuar të udhëtimit
- **Waypoints**: Mbështet pikat e ndërmjetme në rrugë

### Si ta përdorni:

1. Kur krijoni një dërgesë të re, klikoni butonin "Optimizo Rrugën"
2. Sistemi do të llogarisë rrugën optimale dhe do të përditësojë distancën dhe kohën e parashikuar
3. Rruga e optimizuar do të shfaqet në hartë

### Për zhvilluesit:

Për të optimizuar një rrugë, përdorni API-në në `/tracking/api/routes/{route_id}/optimize/`

## 3. Sistemi i Njoftimeve

Sistemi tani ka një sistem të plotë njoftimesh:

- **Njoftime për Nivele të Ulëta Karburanti**: Njofton kur niveli i karburantit bie nën 20%
- **Njoftime për Mirëmbajtje Automjetesh**: Njofton kur një automjet ka nevojë për mirëmbajtje
- **Njoftime për Vonesat në Dërgesa**: Njofton kur një dërgesë vonohet
- **Konfigurime Personale**: Çdo përdorues mund të konfiguroj preferencat e njoftimeve

### Si ta përdorni:

1. Shkoni te **Njoftimet > Lista e Njoftimeve** për të parë të gjitha njoftimet
2. Shkoni te **Njoftimet > Konfigurimet** për të konfiguruar preferencat e njoftimeve
3. Klikoni mbi një njoftim për të parë detajet e tij
4. Përdorni butonin "Shëno si të Lexuar" për të shënuar një njoftim si të lexuar

### Për administratorët:

Për të kontrolluar dhe dërguar njoftime manualisht, ekzekutoni:

```
python manage.py check_notifications
```

## 4. Raportimi dhe Analitika

Sistemi tani ofron raporte dhe analitika të avancuara:

- **Raporti i Konsumit të Karburantit**: Analizon konsumin e karburantit sipas stacioneve dhe llojeve
- **Raporti i Efiçencës së Dërgesave**: Analizon performancën e dërgesave
- **Parashikimi i Nevojave për Karburant**: Parashikon kur një stacion do të ketë nevojë për karburant
- **Ruajtja e Raporteve**: Mundësia për të ruajtur raportet për përdorim të mëvonshëm

### Si ta përdorni:

1. Shkoni te **Analitikë > Raportet e Ruajtura** për të parë raportet e ruajtura
2. Shkoni te **Analitikë > Konsumi i Karburantit** për të gjeneruar raporte për konsumin
3. Shkoni te **Analitikë > Efiçenca e Dërgesave** për të analizuar performancën e dërgesave
4. Shkoni te **Analitikë > Parashikimi i Nevojave** për të parashikuar nevojat për karburant

### Për administratorët:

Për të gjeneruar të dhëna shembull për analitikën, ekzekutoni:

```
python manage.py generate_sample_data --days 30
```

## Konfigurimi i Sistemit

Për të konfiguruar sistemin me të gjitha veçoritë e reja, ndiqni këto hapa:

1. Sigurohuni që të gjitha migrimet janë aplikuar:
   ```
   python manage.py migrate
   ```

2. Ngarkoni të dhënat fillestare për llojet e njoftimeve:
   ```
   python manage.py loaddata notifications/fixtures/notification_types.json
   python manage.py loaddata notifications/fixtures/notification_templates.json
   ```

3. Gjeneroni të dhëna shembull për analitikën:
   ```
   python manage.py generate_sample_data --days 30
   ```

4. Konfiguroni një cron job për të kontrolluar njoftimet rregullisht:
   ```
   # Shembull për crontab (çdo orë)
   0 * * * * cd /path/to/project && python manage.py check_notifications
   ```

## Problemet e Njohura dhe Zgjidhjet

- **WebSocket nuk lidhet**: Sigurohuni që serveri ASGI është duke u ekzekutuar
- **Harta nuk shfaqet**: Kontrolloni nëse API key për hartën është konfiguruar saktë
- **Njoftimet nuk dërgohen**: Kontrolloni konfigurimin e email-it në settings.py

## Zhvillime të Ardhshme

- Aplikacion mobil për shoferët
- Integrim me sisteme GPS të automjeteve
- Raporte më të avancuara dhe parashikime me machine learning
- Integrim me sisteme të tjera të biznesit
