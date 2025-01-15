define('DB_NAME', 'wordpress_db');               // Имя базы данных, используемой WordPress.
define('DB_USER', 'wordpress_user');             // Имя пользователя для подключения к базе данных.
define('DB_PASSWORD', 'secure_password123');     // Пароль для пользователя базы данных.
define('DB_HOST', 'localhost');                   // Если база данных находится на том же сервере

// Включение режима отладки
define('WP_DEBUG', true);                         // Включает режим отладки
define('WP_DEBUG_LOG', true);                     // Записывает ошибки в файл debug.log в wp-content
define('WP_DEBUG_DISPLAY', true);                 // Отображает ошибки на экране
@ini_set('display_errors', 1);                   // Включает отображение ошибок PHP