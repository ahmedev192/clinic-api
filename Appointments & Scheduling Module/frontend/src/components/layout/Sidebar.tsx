import { motion } from 'framer-motion';
import { NavLink } from 'react-router-dom';
import {
  Calendar,
  LayoutDashboard,
  Clock,
  ListChecks,
  Bell,
  UserCog,
  Menu,
  X,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useLanguage } from '@/contexts/LanguageContext';
import { useState } from 'react';
import { cn } from '@/lib/utils';

const menuItems = [
  { 
    icon: LayoutDashboard, 
    label: { en: 'Dashboard', ar: 'لوحة التحكم' }, 
    path: '/' 
  },
  { 
    icon: Calendar, 
    label: { en: 'Appointments', ar: 'المواعيد' }, 
    path: '/appointments' 
  },
  { 
    icon: ListChecks, 
    label: { en: 'Waiting List', ar: 'قائمة الانتظار' }, 
    path: '/waiting-list' 
  },
  { 
    icon: Clock, 
    label: { en: 'Doctor Availability', ar: 'توفر الأطباء' }, 
    path: '/availability' 
  },
  { 
    icon: Bell, 
    label: { en: 'Reminders', ar: 'التذكيرات' }, 
    path: '/reminders' 
  },
  { 
    icon: UserCog, 
    label: { en: 'Settings', ar: 'الإعدادات' }, 
    path: '/settings' 
  },
];

export const Sidebar = () => {
  const { t, direction } = useLanguage();
  const [isCollapsed, setIsCollapsed] = useState(false);

  return (
    <>
      {/* Mobile Menu Button */}
      <Button
        variant="outline"
        size="icon"
        className="fixed top-4 left-4 z-50 md:hidden"
        onClick={() => setIsCollapsed(!isCollapsed)}
      >
        {isCollapsed ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
      </Button>

      {/* Sidebar */}
      <motion.aside
        initial={{ x: direction === 'rtl' ? 100 : -100, opacity: 0 }}
        animate={{ 
          x: 0, 
          opacity: 1,
          width: isCollapsed ? 80 : 260 
        }}
        transition={{ duration: 0.3 }}
        className={cn(
          "fixed top-0 h-screen bg-card border-r border-border z-40",
          "hidden md:block",
          direction === 'rtl' ? 'right-0' : 'left-0'
        )}
      >
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="p-6 border-b border-border">
            <motion.div
              className="flex items-center gap-3"
              whileHover={{ scale: 1.05 }}
            >
              <div className="w-10 h-10 bg-gradient-to-br from-primary to-accent rounded-lg flex items-center justify-center">
                <Calendar className="h-6 w-6 text-white" />
              </div>
              {!isCollapsed && (
                <div>
                  <h2 className="font-bold text-lg text-foreground">
                    {t('clinic', { en: 'Clinic', ar: 'العيادة' })}
                  </h2>
                  <p className="text-xs text-muted-foreground">
                    {t('management', { en: 'Management', ar: 'الإدارة' })}
                  </p>
                </div>
              )}
            </motion.div>
          </div>

          {/* Navigation */}
          <nav className="flex-1 p-4 space-y-2">
            {menuItems.map((item, index) => (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  cn(
                    'flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200',
                    'hover:bg-primary/10',
                    isActive
                      ? 'bg-primary text-primary-foreground shadow-md'
                      : 'text-muted-foreground hover:text-foreground'
                  )
                }
              >
                {({ isActive }) => (
                  <motion.div
                    className="flex items-center gap-3 w-full"
                    initial={{ x: direction === 'rtl' ? 20 : -20, opacity: 0 }}
                    animate={{ x: 0, opacity: 1 }}
                    transition={{ delay: index * 0.05 }}
                    whileHover={{ x: direction === 'rtl' ? -5 : 5 }}
                  >
                    <item.icon className="h-5 w-5 flex-shrink-0" />
                    {!isCollapsed && (
                      <span className="font-medium">
                        {t(item.path, item.label)}
                      </span>
                    )}
                    {isActive && (
                      <motion.div
                        className={cn(
                          'ml-auto w-1 h-6 bg-primary-foreground rounded-full',
                          direction === 'rtl' && 'mr-auto ml-0'
                        )}
                        layoutId="activeIndicator"
                      />
                    )}
                  </motion.div>
                )}
              </NavLink>
            ))}
          </nav>

          {/* Toggle Button */}
          <div className="p-4 border-t border-border">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setIsCollapsed(!isCollapsed)}
              className="w-full"
            >
              <Menu className="h-4 w-4" />
              {!isCollapsed && (
                <span className={direction === 'rtl' ? 'mr-2' : 'ml-2'}>
                  {t('collapse', { en: 'Collapse', ar: 'طي' })}
                </span>
              )}
            </Button>
          </div>
        </div>
      </motion.aside>
    </>
  );
};
