# EduAI - AI-Powered Learning Platform

## � Quick View

https://edu-ai-lilac.vercel.app/

## � Quick Setup

### 1. Install Dependencies
```bash
npm install
```

### 2. Environment Setup
Create a `.env` file in the root directory and add:

```env
VITE_SUPABASE_URL=your_supabase_project_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
```

**Get these values from project owner or:**
1. Go to [Supabase Dashboard](https://supabase.com/dashboard) 
2. Select project → Connect → App frameworks → React → Vite
3. Copy the URL and anon key

### 3. Run the App
```bash
npm run dev
```

App will be available at [http://localhost:5173](http://localhost:5173)

## �️ Development Commands

- `npm run dev` - Start development server
- `npm run build` - Build for production  
- `npm run lint` - Run ESLint

## � Key Files

- `src/components/LandingPage.jsx` - Main landing page
- `src/components/AuthModal.jsx` - Authentication modal
- `src/hooks/useAuth.js` - Authentication logic
- `src/supabase.jsx` - Database connection
