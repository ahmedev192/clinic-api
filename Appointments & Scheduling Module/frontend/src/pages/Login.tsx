import { useState } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Calendar, Loader2 } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { useLanguage } from '@/contexts/LanguageContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { LanguageSwitcher } from '@/components/LanguageSwitcher';
import { toast } from 'sonner';

export default function Login() {
  const { login } = useAuth();
  const { t } = useLanguage();
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      await login(username, password);
      toast.success(t('login_success', { en: 'Login successful!', ar: 'تم تسجيل الدخول بنجاح!' }));
      navigate('/');
    } catch (error: any) {
      toast.error(
        t('login_error', {
          en: error.response?.data?.message || 'Invalid credentials',
          ar: 'بيانات الاعتماد غير صحيحة',
        })
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-background via-primary/5 to-accent/10 p-4">
      <div className="absolute top-4 right-4">
        <LanguageSwitcher />
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-md"
      >
        <Card className="shadow-2xl">
          <CardHeader className="text-center space-y-4">
            <motion.div
              className="mx-auto w-20 h-20 bg-gradient-to-br from-primary to-accent rounded-2xl flex items-center justify-center shadow-lg"
              whileHover={{ scale: 1.05, rotate: 5 }}
              transition={{ duration: 0.3 }}
            >
              <Calendar className="h-10 w-10 text-white" />
            </motion.div>
            <div>
              <CardTitle className="text-2xl font-bold">
                {t('welcome_back', { en: 'Welcome Back', ar: 'مرحباً بعودتك' })}
              </CardTitle>
              <CardDescription className="mt-2">
                {t('login_subtitle', {
                  en: 'Sign in to your clinic management account',
                  ar: 'قم بتسجيل الدخول إلى حساب إدارة العيادة',
                })}
              </CardDescription>
            </div>
          </CardHeader>

          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="username">
                  {t('username', { en: 'Username', ar: 'اسم المستخدم' })}
                </Label>
                <Input
                  id="username"
                  type="text"
                  placeholder={t('username_placeholder', {
                    en: 'Enter your username',
                    ar: 'أدخل اسم المستخدم',
                  })}
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                  disabled={isLoading}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="password">
                  {t('password', { en: 'Password', ar: 'كلمة المرور' })}
                </Label>
                <Input
                  id="password"
                  type="password"
                  placeholder={t('password_placeholder', {
                    en: 'Enter your password',
                    ar: 'أدخل كلمة المرور',
                  })}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  disabled={isLoading}
                />
              </div>

              <Button type="submit" className="w-full" disabled={isLoading}>
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    {t('logging_in', { en: 'Logging in...', ar: 'جاري تسجيل الدخول...' })}
                  </>
                ) : (
                  t('login', { en: 'Login', ar: 'تسجيل الدخول' })
                )}
              </Button>
            </form>
          </CardContent>
        </Card>

        <motion.p
          className="text-center text-sm text-muted-foreground mt-6"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
        >
          {t('demo_credentials', {
            en: 'Demo: username / password',
            ar: 'تجريبي: username / password',
          })}
        </motion.p>
      </motion.div>
    </div>
  );
}
