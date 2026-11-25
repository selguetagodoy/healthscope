"""Conservative public-facing press selection; retains raw captures for review."""
import re
import unicodedata

def public_press(record):
    if record.get("source_type") != "Prensa":
        return True
    if record.get("status") == "Verificado":
        return True
    text = "".join(c for c in unicodedata.normalize("NFD", str(record.get("title", "")).lower()) if not unicodedata.combining(c))
    if re.search(r"encuentro pagado|entretenimiento digital|dupla televisiva", text):
        return False
    return bool(re.search(r"\b(?:ges|lrs|isp|fonasa|isapres?|cenabast|minsal|dipres|inapi)\b|proyecto de ley|politica sanitaria|regulacion sanitaria|presupuesto|financiamiento|medicament|farmaceutic|farmacia|farmacovigilancia|ensayo clinico|ricarte soto|enfermedades raras|fibrosis quistica|alto costo|listas? de espera|vacunacion|telemedicina|prestacion|acceso a la salud|remuneraciones en salud|datos (?:de salud|clinicos)|informacion medica|compra publica|licitacion|abastecimiento|patente", text))
