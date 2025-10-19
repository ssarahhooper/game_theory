python3 -m venv venv
source venv/bin/activate
pip install networkx matplotlib numpy scipy
python traffic_analysis.py traffic.gml 4 0 3 --plot
