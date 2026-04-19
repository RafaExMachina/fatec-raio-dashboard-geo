# 📍 FATEC Radius Dashboard with Valid Region

## 🎯 Objective
This project provides an interactive web application to analyze geographic coverage using a fixed radius.

Given a central coordinate and a radius (e.g., 30 km), the application:

- Identifies all points within the radius
- Computes the **valid region** where the center can move without losing current coverage
- Displays results on interactive maps

---

## 🧠 Key Concept

For each point inside the radius, we create a circle of the same radius.

The valid region is:

Intersection of all these circles

This represents:
> All possible positions where the center can move while still covering the same points

---

## 🚀 Features

- 🗺️ Interactive map with radius visualization
- 📍 Points classification (inside / outside radius)
- 🟢 Computation of **valid region**
- 📐 High-precision geometry using UTM projection
- ⚡ Fast and responsive interface with Streamlit

---

## 🛠️ Technologies Used

- Python
- Streamlit
- Folium
- Shapely
- PyProj
- Geopy
- Pandas

---

## 📦 Project Structure

```
fatec-raio-dashboard/
│
├── app.py
├── requirements.txt
├── data/
│   └── fatec_enderecos_geocodificados.json
```

---

## ⚙️ Installation

```bash
pip install -r requirements.txt
```

---

## ▶️ Running the App

```bash
streamlit run app.py
```

---

## 🌐 Deployment

This app can be deployed easily using:

- Streamlit Cloud

---

## 📊 Applications

This model can be applied to:

- 📡 Antenna coverage analysis
- 🚗 Logistics and delivery zones
- 🏥 Service area planning
- 📍 Optimal facility placement

---

## ⚠️ Notes

- Uses geographic projection (UTM) for high accuracy
- Avoids distortions from latitude/longitude calculations

---

## 👨‍💻 Author

Rafael Costa  
PhD in Electrical Engineering  
Focus: Machine Learning, DSP, and Spatial Analysis

---

## 📌 Future Improvements

- Optimal center calculation
- Coverage maximization
- Heatmaps of feasible regions
- Integration with real routing APIs

---

## 📄 License

This project is open-source and free to use.
