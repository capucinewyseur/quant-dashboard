import yfinance as yf
import pandas as pd

def load_asset(ticker, start="2018-01-01", end=None, interval="1d"):
    """
    Charge les données d'un actif depuis Yahoo Finance et calcule les rendements
    
    Args:
        ticker: Symbole de l'actif (ex: "AAPL")
        start: Date de début (format "YYYY-MM-DD")
        end: Date de fin (format "YYYY-MM-DD" ou None pour aujourd'hui)
        interval: Intervalle des données ("1d", "1h", "1m", etc.)
    
    Returns:
        DataFrame avec les colonnes: Open, High, Low, Close, Volume, return
        Retourne un DataFrame vide en cas d'erreur
    """
    try:
        # Vérifier que le ticker n'est pas vide
        if not ticker or not isinstance(ticker, str) or len(ticker.strip()) == 0:
            return pd.DataFrame()
        
        # Télécharger les données depuis Yahoo Finance
        df = yf.download(ticker, start=start, end=end, interval=interval, progress=False, show_errors=False)
        
        # Vérifier si les données sont vides
        if df.empty:
            return pd.DataFrame()
        
        # Si MultiIndex, aplatir les colonnes
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.droplevel(1)
        
        # Vérifier que les colonnes nécessaires existent
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        if not all(col in df.columns for col in required_columns):
            return pd.DataFrame()
        
        df = df[required_columns].copy()
        
        # Nettoyer les NaN
        df.dropna(inplace=True)
        
        # Vérifier qu'il reste des données après nettoyage
        if df.empty:
            return pd.DataFrame()
        
        # Calculer les rendements journaliers
        df["return"] = df["Close"].pct_change()
        
        # Nettoyer les NaN créés par pct_change
        df.dropna(inplace=True)
        
        # Vérification finale
        if df.empty:
            return pd.DataFrame()
        
        return df
        
    except Exception as e:
        # En cas d'erreur (API down, ticker invalide, etc.), retourner un DataFrame vide
        return pd.DataFrame()

