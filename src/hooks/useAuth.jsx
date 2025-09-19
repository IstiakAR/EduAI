import { useEffect, useState, createContext, useContext } from 'react';
import supabase from '../supabase';

const AuthContext = createContext({});

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    console.log('useAuth useEffect started');
    console.log('Supabase config check:', {
      url: import.meta.env.VITE_SUPABASE_URL ? 'Set' : 'Missing',
      key: import.meta.env.VITE_SUPABASE_ANON_KEY ? 'Set' : 'Missing'
    });
    
    // Get initial session
    const getInitialSession = async () => {
      try {
        console.log('Getting initial session...');
        const { data: { session }, error } = await supabase.auth.getSession();
        if (error) {
          console.error('Error getting session:', error);
        } else {
          console.log('Session retrieved:', session?.user?.id || 'No user');
          setUser(session?.user || null);
          if (session?.user) {
            await createUserProfile(session.user);
          }
        }
      } catch (error) {
        console.error('Error in getInitialSession:', error);
      } finally {
        console.log('Setting loading to false');
        setLoading(false);
      }
    };

    getInitialSession();

    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event, session) => {
        console.log('Auth state changed:', event, session?.user?.id);
        setUser(session?.user || null);
        setLoading(false);
        
        if (event === 'SIGNED_IN' && session?.user) {
          await createUserProfile(session.user);
        }
      }
    );

    return () => subscription.unsubscribe();
  }, []);

  const value = {
    user,
    loading,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

export function useUserId() {
  const { user } = useAuth();
  console.log('useUserId called - user:', user?.id);
  
  if (user?.id) {
    console.log('Returning authenticated user ID:', user.id);
    return user.id;
  }
  
  const demoUser = localStorage.getItem('demo_user');
  if (demoUser) {
    const parsedUser = JSON.parse(demoUser);
    console.log('Returning demo user ID from localStorage:', parsedUser.id);
    return parsedUser.id;
  }
  
  const demoUserId = crypto.randomUUID();
  console.log('Creating new demo user ID:', demoUserId);
  localStorage.setItem('demo_user', JSON.stringify({ id: demoUserId }));
  return demoUserId;
}

const createUserProfile = async (user) => {
  try {
    const { data: existingUser, error: fetchError } = await supabase
      .from('users')
      .select('user_id')
      .eq('user_id', user.id)
      .single();

    if (fetchError && fetchError.code !== 'PGRST116') {
      console.error('Error checking existing user:', fetchError);
      return;
    }

    if (!existingUser) {
      const { error: insertError } = await supabase
        .from('users')
        .insert({
          user_id: user.id,
          display_name: user.user_metadata?.display_name || user.user_metadata?.full_name || user.email?.split('@')[0] || 'User',
          avatar_url: user.user_metadata?.avatar_url || null,
          preferences: {},
        });

      if (insertError) {
        console.error('Error creating user profile:', insertError);
      } else {
        console.log('User profile created successfully');
      }
    }
  } catch (err) {
    console.error('Error in createUserProfile:', err);
  }
};