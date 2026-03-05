# FitFlow 💪

A full-stack fitness tracking web application built with Django REST Framework and vanilla HTML/CSS/JavaScript.

## 🌐 Live Demo

- **Frontend:** https://fitflow-api-g4kx.vercel.app/login.html
- **Backend API:** https://fitflow-api-production-c25a.up.railway.app/api/
- **Demo Account:** `livetest01` / `FitFlow2026!`

## 📋 Project Overview

FitFlow is a fitness tracking platform that allows users to log workouts, track body weight progress, view personal records, browse an exercise library, and engage with a community through social posts and challenges.

## ✨ Features

- **User Authentication** — Register, login, logout with token-based auth
- **Workout Logging** — Log sessions with exercises, sets, reps and weight
- **Exercise Library** — Browse 100+ exercises from wger API by muscle group
- **Progress Tracking** — Weight history charts and personal records
- **Dashboard** — Weekly volume, total workouts, PRs and body weight stats
- **Social Feed** — Community posts and activity
- **Challenges** — Join fitness challenges and compete with others
- **Mobile Responsive** — Works on all screen sizes with bottom navigation

## 🛠️ Tech Stack

### Backend
- **Django 4.x** — Web framework
- **Django REST Framework** — API development
- **PostgreSQL** — Production database (Railway)
- **Token Authentication** — Secure user sessions
- **wger API** — Exercise database integration

### Frontend
- **HTML5 / CSS3 / Vanilla JavaScript** — No frameworks
- **Chart.js** — Progress and volume charts
- **DM Sans + Syne** — Typography (Google Fonts)
- **Vercel** — Frontend hosting

### Deployment
- **Railway** — Backend + PostgreSQL database
- **Vercel** — Frontend static hosting
- **GitHub** — Version control

## 📁 Project Structure

```
fitflow-api/
├── fitflow_api/          # Django project settings
├── users/                # User auth & profiles
├── workouts/             # Workout & exercise models
├── progress/             # Weight logs & PRs
├── social/               # Feed & challenges
├── frontend/             # HTML frontend
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── workouts.html
│   ├── log-workout.html
│   ├── exercises.html
│   ├── progress.html
│   ├── profile.html
│   ├── social.html
│   ├── challenges.html
│   └── api.js
└── README.md
```

## 🔗 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register/` | Register new user |
| POST | `/api/auth/login/` | Login user |
| GET/PUT | `/api/auth/profile/` | Get/update profile |
| GET/POST | `/api/workouts/workouts/` | List/create workouts |
| GET/POST | `/api/workouts/exercises/` | List exercises |
| GET/POST | `/api/workouts/sets/` | Log exercise sets |
| GET/POST | `/api/progress/weight/` | Weight logs |
| GET | `/api/progress/prs/` | Personal records |
| GET | `/api/progress/dashboard/` | Dashboard stats |
| GET | `/api/social/feed/` | Social feed |
| GET | `/api/social/challenges/` | Challenges |

## 🗄️ Database Models

- **User** — Extended Django user with height, weight, fitness goal
- **Exercise** — Name, muscle group, equipment, difficulty
- **WorkoutSession** — Date, duration, notes, user reference
- **ExerciseSet** — Sets, reps, weight linked to workout and exercise
- **WeightEntry** — Body weight logs with date
- **PersonalRecord** — Best weight per exercise per user
- **SocialPost** — Community feed posts
- **Challenge** — Fitness challenges with participants

## 🚀 Setup & Installation

### Backend

```bash
git clone https://github.com/LifeofaBlvckman/fitflow-api.git
cd fitflow-api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Environment Variables

```
DJANGO_SECRET_KEY=your-secret-key
DATABASE_URL=your-postgres-url
DEBUG=False
ALLOWED_HOSTS=your-domain.com
```

### Frontend

Open any `.html` file from the `frontend/` folder via a local server:

```bash
cd frontend
python3 -m http.server 3000
# Open http://localhost:3000/login.html
```

## 👤 Author

**Olaoluwa** — ALX Backend Engineering Program  
GitHub: [@LifeofaBlvckman](https://github.com/LifeofaBlvckman)
