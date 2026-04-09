import { ref } from "vue";

const LANGUAGE_STORAGE_KEY = "baltctf_language";

function readStoredLanguage() {
  try {
    const stored = window.localStorage.getItem(LANGUAGE_STORAGE_KEY);
    return stored === "ru" ? "ru" : "en";
  } catch {
    return "en";
  }
}

export const currentLanguage = ref(readStoredLanguage());

export const languageOptions = [
  { code: "en", label: "English" },
  { code: "ru", label: "Русский" }
];

const messages = {
  en: {
    nav: {
      dashboard: "Dashboard",
      services: "Service Status",
      team: "Team Profile",
      admin: "Admin Tools"
    },
    shell: {
      eyebrow: "BaltCTF Platform",
      title: "Attack/Defense control room",
      guestSession: "Guest session",
      operatorAccount: "Operator account",
      guestHint: "Use Team Profile for sign-in and registration",
      language: "Language"
    },
    notice: {
      connection: "Connection issue.",
      account: "Account flow.",
      reservation: "Reservation flow.",
      admin: "Admin console.",
      flag: "Flag result.",
      team: "Team tools."
    },
    common: {
      independent: "Independent",
      notSet: "not set",
      unknown: "Unknown",
      unknownTeam: "unknown team",
      unknownService: "unknown service",
      unknownTarget: "Unknown target",
      noCheckerNote: "No checker note.",
      noData: "No data",
      points: "{count} pts",
      membersCount: "{count} member(s)",
      registeredCount: "{count} registered",
      roundLabel: "Round {number}",
      since: "{state} since {date}",
      expiresAt: "Expires {date}",
      noExpiration: "No expiration set",
      yes: "Yes",
      no: "No"
    },
    role: {
      captain: "Captain",
      player: "Player"
    },
    moderation: {
      approved: "Approved",
      pending: "Pending",
      suspended: "Suspended"
    },
    reservationStatus: {
      pending: "Pending",
      approved: "Approved",
      rejected: "Rejected",
      claimed: "Claimed"
    },
    roundState: {
      planned: "Planned",
      running: "Running",
      finished: "Finished"
    },
    submissionState: {
      pending: "Pending",
      accepted: "Accepted",
      rejected: "Rejected"
    },
    serviceState: {
      up: "Up",
      mumble: "Mumble",
      corrupt: "Corrupt",
      down: "Down",
      unknown: "No data"
    },
    dashboard: {
      heroEyebrow: "Attack / Defense CTF Dashboard",
      heroTitle: "BaltCTF live control room",
      heroLead:
        "The platform now covers the first real competition workflow: teams can register, participants can authenticate, and authenticated users can submit captured flags through the web interface.",
      refresh: "Refresh feed",
      refreshing: "Refreshing...",
      waitingRound: "Waiting for first round",
      waitingRoundMeta:
        "Create rounds or load demo data to populate the control room.",
      metrics: {
        teams: "Teams",
        teamsNote: "approved squads currently competing",
        users: "Users",
        usersNote: "registered participants",
        services: "Services",
        servicesNote: "demo vulnbox services under monitoring",
        rounds: "Rounds",
        roundsNote: "planned or completed round records",
        acceptedFlags: "Accepted flags",
        acceptedFlagsNote: "successful attack submissions"
      },
      stateLoading:
        "Loading backend data for the scoreboard, service states, and attack feed.",
      stateEmptyTitle: "Dashboard is ready but the platform has no data yet",
      stateEmptyMessage:
        "Run migrations and load demo fixtures to see a full scoreboard preview:"
    },
    board: {
      scoreboardKicker: "Scoreboard",
      scoreboardTitle: "Current team ranking",
      leader: "Leader",
      team: "Team",
      attack: "Attack",
      defense: "Defense",
      total: "Total",
      serviceStatusKicker: "Service Status",
      serviceStatusTitle: "Current round service posture",
      rankOnBoard: "#{rank} on the board",
      attackFeedKicker: "Attack Feed",
      attackFeedTitle: "Recent submissions",
      targetVia: "Target: {team} via {service}"
    },
    timeline: {
      kicker: "Timeline",
      title: "Recent rounds"
    },
    pages: {
      team: {
        kicker: "Team Portal",
        title: "Registration, roster, and flag submission",
        registrationOpen: "Registration window is currently open.",
        registrationClosed: "Registration window is currently closed.",
        noTeamTitle: "No team linked to this account",
        noTeamMessage:
          "This account can still be used for operator or admin tasks, but it cannot submit flags."
      },
      services: {
        kicker: "Checker Matrix",
        title: "Service health across all approved teams",
        meta: "Live checker feedback for Atlas Board, Signal API, and Cold Storage.",
        loading: "Loading the latest checker results from the backend."
      },
      admin: {
        kicker: "Admin Tools",
        title: "Registration control, moderation, and round orchestration",
        meta:
          "Staff-only workflows for team moderation, reservation approvals, and checker lifecycle.",
        authTitle: "Admin access requires authentication",
        authMessage:
          "Sign in with a staff account to manage registration windows, rounds, and reservations.",
        staffTitle: "Staff access required",
        staffMessage:
          "This account can view team tools, but admin workflows are restricted to staff operators."
      }
    },
    serviceMatrix: {
      kicker: "Service Status",
      titleWithRound: "Round {number} availability",
      titleWaiting: "Waiting for a running round",
      noData: "No approved teams or status checks have been recorded yet.",
      team: "Team"
    },
    guest: {
      reservationKicker: "Registration window",
      reservationTitle: "Reserve a team name",
      windowOpen: "Window open",
      windowClosed: "Window closed",
      reservationRequired:
        "This event requires an approved reservation token before team registration.",
      reservationOptional:
        "Reservations are optional, but they reserve the team name and provide a traceable approval flow.",
      teamName: "Team name",
      preferredSlug: "Preferred slug",
      captainUsername: "Captain username",
      contactEmail: "Contact email",
      requestReservation: "Request reservation",
      submitting: "Submitting...",
      authKicker: "Authentication",
      signInTitle: "Sign in",
      username: "Username",
      password: "Password",
      signIn: "Sign in",
      signingIn: "Signing in...",
      registrationKicker: "Registration",
      createTeamTitle: "Create a team",
      maxMembers: "Up to {count} members including captain",
      registrationClosedHint:
        "Registration is currently closed. Wait for the next window or contact an operator.",
      reservationTokenRequiredHint:
        "Reservation token is required. Request or paste an approved token below before submitting.",
      teamSlug: "Team slug",
      affiliation: "Affiliation",
      reservationToken: "Reservation token",
      reservationTokenPlaceholder:
        "Paste approved token if the registration window requires it",
      captain: "Captain",
      email: "Email",
      firstName: "First name",
      lastName: "Last name",
      participants: "Participants",
      addParticipant: "Add participant",
      participantsHint:
        "Add optional teammates now, or register only the captain and create the rest later.",
      playerLabel: "Player {index}",
      remove: "Remove",
      creatingTeam: "Creating team...",
      registerTeam: "Register team"
    },
    workspace: {
      teamSession: "Team Session",
      operatorSession: "Operator Session",
      logout: "Logout",
      signedInAs: "Signed in as",
      signedInSummary: "{role} for {affiliation}",
      memberCounter: "{current}/{max} members",
      contact: "Contact",
      moderation: "Moderation",
      moderationNoteFallback: "No moderation note from the organizers.",
      noTeamAccount:
        "This account is not assigned to a playing team. Use it for operator or administrator workflows such as managing rounds, teams, and services.",
      roster: "Roster",
      promote: "Promote",
      demote: "Demote",
      captainTools: "Captain tools",
      teamProfile: "Team profile",
      save: "Save",
      saving: "Saving...",
      updateTeamProfile: "Update team profile",
      addMember: "Add member",
      teamLimitReached:
        "Team size limit reached. Remove a player or change the limit in the backend configuration before adding someone else.",
      adding: "Adding...",
      addPlayer: "Add player",
      flagSubmission: "Flag Submission",
      operatorMode: "Operator Mode",
      submitCapturedFlags: "Submit captured flags",
      competitionControls: "Competition controls",
      flagValue: "Flag value",
      submitFlag: "Submit flag",
      teamActivity: "Team activity",
      noSubmissions: "No submissions yet for this team.",
      activityLine: "{target} via {service}",
      flagDisabled:
        "Flag submission is disabled for non-team accounts. If this is a staff user, the admin console below can be used to create teams and services, prepare new rounds, start or finish them, and generate flags."
    },
    admin: {
      registrationKicker: "Registration",
      registrationTitle: "Window, approval, and scheduling rules",
      registrationOpen: "Registration open",
      reservationRequired: "Reservation required",
      autoApprove: "Auto-approve registrations",
      registrationStarts: "Registration starts",
      registrationEnds: "Registration ends",
      roundDuration: "Round duration (min)",
      breakDuration: "Break duration (min)",
      saveSettings: "Save competition settings",
      reservationsKicker: "Reservations",
      reservationsTitle: "Approve or reject team names",
      reservationsEmpty: "No pending or recent reservation requests yet.",
      approve: "Approve",
      reject: "Reject",
      active: "Active",
      disabled: "Disabled",
      teamsKicker: "Teams",
      teamsTitle: "Manage teams",
      name: "Name",
      createTeam: "Create team",
      markPending: "Mark pending",
      suspend: "Suspend",
      disable: "Disable",
      enable: "Enable",
      delete: "Delete",
      servicesKicker: "Services",
      servicesTitle: "Manage services",
      port: "Port",
      portUnset: "Port not set",
      description: "Description",
      createService: "Create service",
      roundsKicker: "Rounds",
      roundsTitle: "Competition lifecycle",
      nextSuggestedRound: "Next suggested round: {number}",
      runningRoundReady: "Round {number} is ready for checker ticks",
      noRunningRound: "No running round available for checker ticks",
      lastCheckerReport: "Last checker report: {date}",
      noCheckerReport: "No checker report has been recorded for the active round yet.",
      runCheckerTick: "Run checker tick",
      roundNumber: "Round number",
      scheduleCount: "Schedule count",
      scheduleStart: "Schedule start",
      createPlannedRound: "Create planned round",
      scheduleBatch: "Schedule round batch",
      start: "Start",
      finish: "Finish",
      generateFlags: "Generate flags",
      serviceGeneratedFlags: "{count} generated flag(s)",
      teamMeta: "{count} member(s) · {moderation}",
      roundGeneratedFlags: "{count} flag(s) generated",
      working: "Working..."
    },
    prompts: {
      removeMember: 'Remove "{username}" from the team?',
      deleteTeam: 'Delete team "{name}"? This will remove related competition data.',
      deleteService: 'Delete service "{name}"?',
      moderationNote: 'Moderation note for "{name}"',
      rejectReservation: 'Rejection note for "{name}"'
    },
    messages: {
      signedInAs: "Signed in as {username}.",
      sessionClosed: "Session closed.",
      teamRegistered: "Team registration completed.",
      reservationCreated: "Team name reservation request created.",
      teamProfileUpdated: "Team profile updated.",
      teamMemberAdded: "Team member added.",
      memberRoleUpdated: "Member role updated.",
      memberRemoved: "Member removed.",
      flagSubmitted: "Flag submitted.",
      adminActionCompleted: "Admin action completed.",
      teamCreated: "Team created.",
      teamUpdated: "Team updated.",
      serviceCreated: "Service created.",
      serviceUpdated: "Service updated.",
      roundCreated: "Planned round created.",
      roundStarted: "Round started.",
      roundFinished: "Round finished.",
      flagsGenerated: "Flags generated.",
      checkerTickCompleted: "Checker tick completed.",
      competitionSettingsUpdated: "Competition settings updated.",
      roundsScheduled: "Round batch scheduled.",
      reservationApproved: "Reservation approved.",
      reservationRejected: "Reservation rejected.",
      authRestoreFailed: "Unable to restore the session.",
      dashboardLoadFailed: "Unable to load the BaltCTF dashboard.",
      servicesLoadFailed: "Unable to load the service status matrix.",
      registrationSettingsFailed: "Unable to load registration settings.",
      loginFailed: "Unable to sign in.",
      registerFailed: "Unable to register the team.",
      reservationFailed: "Unable to create the reservation.",
      flagSubmitFailed: "Unable to submit the flag.",
      teamProfileFailed: "Unable to update the team profile.",
      addMemberFailed: "Unable to add the team member.",
      updateRoleFailed: "Unable to update the member role.",
      removeMemberFailed: "Unable to remove the member.",
      adminStateFailed: "Unable to load admin state.",
      adminActionFailed: "Admin action failed."
    }
  },
  ru: {
    nav: {
      dashboard: "Дашборд",
      services: "Статусы сервисов",
      team: "Профиль команды",
      admin: "Админ-инструменты"
    },
    shell: {
      eyebrow: "Платформа BaltCTF",
      title: "Центр управления Attack/Defense",
      guestSession: "Гостевая сессия",
      operatorAccount: "Операторский аккаунт",
      guestHint: "Для входа и регистрации откройте раздел профиля команды",
      language: "Язык"
    },
    notice: {
      connection: "Проблема с подключением.",
      account: "Аккаунт.",
      reservation: "Резервирование.",
      admin: "Админ-консоль.",
      flag: "Результат флага.",
      team: "Инструменты команды."
    },
    common: {
      independent: "Независимая команда",
      notSet: "не задано",
      unknown: "Неизвестно",
      unknownTeam: "неизвестная команда",
      unknownService: "неизвестный сервис",
      unknownTarget: "Неизвестная цель",
      noCheckerNote: "Нет заметки от чекера.",
      noData: "Нет данных",
      points: "{count} очк.",
      membersCount: "{count} участн.",
      registeredCount: "{count} зарегистр.",
      roundLabel: "Раунд {number}",
      since: "{state} с {date}",
      expiresAt: "Истекает {date}",
      noExpiration: "Срок не задан",
      yes: "Да",
      no: "Нет"
    },
    role: {
      captain: "Капитан",
      player: "Игрок"
    },
    moderation: {
      approved: "Одобрена",
      pending: "На модерации",
      suspended: "Приостановлена"
    },
    reservationStatus: {
      pending: "Ожидает",
      approved: "Одобрено",
      rejected: "Отклонено",
      claimed: "Использовано"
    },
    roundState: {
      planned: "Запланирован",
      running: "Идёт",
      finished: "Завершён"
    },
    submissionState: {
      pending: "Ожидает",
      accepted: "Принят",
      rejected: "Отклонён"
    },
    serviceState: {
      up: "Доступен",
      mumble: "Нестабилен",
      corrupt: "Повреждён",
      down: "Недоступен",
      unknown: "Нет данных"
    },
    dashboard: {
      heroEyebrow: "Панель Attack / Defense CTF",
      heroTitle: "Операционный центр BaltCTF",
      heroLead:
        "Платформа уже закрывает первый реальный соревновательный сценарий: команды могут регистрироваться, участники могут входить в систему, а авторизованные игроки могут сдавать найденные флаги через веб-интерфейс.",
      refresh: "Обновить ленту",
      refreshing: "Обновление...",
      waitingRound: "Ожидание первого раунда",
      waitingRoundMeta:
        "Создайте раунды или загрузите демо-данные, чтобы наполнить панель управления.",
      metrics: {
        teams: "Команды",
        teamsNote: "одобренные команды в соревновании",
        users: "Пользователи",
        usersNote: "зарегистрированные участники",
        services: "Сервисы",
        servicesNote: "demo vulnbox-сервисы под мониторингом",
        rounds: "Раунды",
        roundsNote: "запланированные и завершённые раунды",
        acceptedFlags: "Принятые флаги",
        acceptedFlagsNote: "успешные атакующие сабмиты"
      },
      stateLoading:
        "Загружаются scoreboard, статусы сервисов и лента атак.",
      stateEmptyTitle: "Платформа готова, но данных пока нет",
      stateEmptyMessage:
        "Прогоните миграции и загрузите демо-фикстуры, чтобы увидеть табло:"
    },
    board: {
      scoreboardKicker: "Таблица результатов",
      scoreboardTitle: "Текущий рейтинг команд",
      leader: "Лидер",
      team: "Команда",
      attack: "Атака",
      defense: "Защита",
      total: "Итого",
      serviceStatusKicker: "Статусы сервисов",
      serviceStatusTitle: "Состояние сервисов в текущем раунде",
      rankOnBoard: "#{rank} в таблице",
      attackFeedKicker: "Лента атак",
      attackFeedTitle: "Последние сабмиты",
      targetVia: "Цель: {team} через {service}"
    },
    timeline: {
      kicker: "Таймлайн",
      title: "Последние раунды"
    },
    pages: {
      team: {
        kicker: "Портал команды",
        title: "Регистрация, состав и отправка флагов",
        registrationOpen: "Окно регистрации сейчас открыто.",
        registrationClosed: "Окно регистрации сейчас закрыто.",
        noTeamTitle: "К этому аккаунту не привязана команда",
        noTeamMessage:
          "Такой аккаунт всё ещё можно использовать для операторских или админских задач, но он не может отправлять флаги."
      },
      services: {
        kicker: "Матрица чекера",
        title: "Состояние сервисов всех одобренных команд",
        meta: "Живые результаты чекера для Atlas Board, Signal API и Cold Storage.",
        loading: "Загружаются последние результаты чекера с backend."
      },
      admin: {
        kicker: "Админ-инструменты",
        title: "Управление регистрацией, модерацией и раундами",
        meta:
          "Сценарии только для staff-пользователей: модерация команд, одобрение резервирований и управление жизненным циклом checker.",
        authTitle: "Для доступа к админке нужна авторизация",
        authMessage:
          "Войдите под staff-аккаунтом, чтобы управлять окнами регистрации, раундами и резервированиями.",
        staffTitle: "Нужен staff-доступ",
        staffMessage:
          "Этот аккаунт может видеть командные инструменты, но админские сценарии доступны только staff-операторам."
      }
    },
    serviceMatrix: {
      kicker: "Статусы сервисов",
      titleWithRound: "Доступность сервисов в раунде {number}",
      titleWaiting: "Ожидание запущенного раунда",
      noData: "Пока нет одобренных команд или результатов проверки.",
      team: "Команда"
    },
    guest: {
      reservationKicker: "Окно регистрации",
      reservationTitle: "Зарезервировать имя команды",
      windowOpen: "Окно открыто",
      windowClosed: "Окно закрыто",
      reservationRequired:
        "Для этого соревнования нужен одобренный reservation token до регистрации команды.",
      reservationOptional:
        "Резервирование необязательно, но оно закрепляет имя команды и даёт понятный approval flow.",
      teamName: "Название команды",
      preferredSlug: "Желаемый slug",
      captainUsername: "Логин капитана",
      contactEmail: "Контактный email",
      requestReservation: "Запросить резервирование",
      submitting: "Отправка...",
      authKicker: "Аутентификация",
      signInTitle: "Войти",
      username: "Логин",
      password: "Пароль",
      signIn: "Войти",
      signingIn: "Вход...",
      registrationKicker: "Регистрация",
      createTeamTitle: "Создать команду",
      maxMembers: "До {count} участников вместе с капитаном",
      registrationClosedHint:
        "Регистрация сейчас закрыта. Дождитесь следующего окна или свяжитесь с оператором.",
      reservationTokenRequiredHint:
        "Нужен reservation token. Запросите его или вставьте уже одобренный токен перед отправкой формы.",
      teamSlug: "Slug команды",
      affiliation: "Аффилиация",
      reservationToken: "Токен резервирования",
      reservationTokenPlaceholder:
        "Вставьте одобренный токен, если он требуется для регистрации",
      captain: "Капитан",
      email: "Email",
      firstName: "Имя",
      lastName: "Фамилия",
      participants: "Участники",
      addParticipant: "Добавить участника",
      participantsHint:
        "Можно добавить сокомандников сразу или зарегистрировать только капитана и позже дозаполнить состав.",
      playerLabel: "Игрок {index}",
      remove: "Удалить",
      creatingTeam: "Создание команды...",
      registerTeam: "Зарегистрировать команду"
    },
    workspace: {
      teamSession: "Сессия команды",
      operatorSession: "Операторская сессия",
      logout: "Выйти",
      signedInAs: "Вход выполнен как",
      signedInSummary: "{role} команды {affiliation}",
      memberCounter: "{current}/{max} участников",
      contact: "Контакт",
      moderation: "Модерация",
      moderationNoteFallback: "Нет заметки от организаторов.",
      noTeamAccount:
        "Этот аккаунт не привязан к игровой команде. Используйте его для операторских и административных сценариев: управление раундами, командами и сервисами.",
      roster: "Состав",
      promote: "Повысить",
      demote: "Понизить",
      captainTools: "Инструменты капитана",
      teamProfile: "Профиль команды",
      save: "Сохранить",
      saving: "Сохранение...",
      updateTeamProfile: "Обновить профиль команды",
      addMember: "Добавить участника",
      teamLimitReached:
        "Достигнут лимит команды. Удалите игрока или измените лимит на backend, прежде чем добавлять нового.",
      adding: "Добавление...",
      addPlayer: "Добавить игрока",
      flagSubmission: "Отправка флагов",
      operatorMode: "Режим оператора",
      submitCapturedFlags: "Отправить найденные флаги",
      competitionControls: "Управление соревнованием",
      flagValue: "Значение флага",
      submitFlag: "Отправить флаг",
      teamActivity: "Активность команды",
      noSubmissions: "У этой команды пока нет сабмитов.",
      activityLine: "{target} через {service}",
      flagDisabled:
        "Отправка флагов недоступна для аккаунтов без команды. Если это staff-пользователь, используйте админ-консоль ниже для создания команд и сервисов, подготовки новых раундов, их запуска или остановки и генерации флагов."
    },
    admin: {
      registrationKicker: "Регистрация",
      registrationTitle: "Окна регистрации, правила одобрения и расписание",
      registrationOpen: "Регистрация открыта",
      reservationRequired: "Нужно резервирование",
      autoApprove: "Автоодобрение регистраций",
      registrationStarts: "Старт регистрации",
      registrationEnds: "Конец регистрации",
      roundDuration: "Длительность раунда (мин)",
      breakDuration: "Перерыв между раундами (мин)",
      saveSettings: "Сохранить настройки соревнования",
      reservationsKicker: "Резервирования",
      reservationsTitle: "Одобрение и отклонение имён команд",
      reservationsEmpty: "Пока нет новых или недавних заявок на резервирование.",
      approve: "Одобрить",
      reject: "Отклонить",
      active: "Активна",
      disabled: "Выключена",
      teamsKicker: "Команды",
      teamsTitle: "Управление командами",
      name: "Название",
      createTeam: "Создать команду",
      markPending: "На модерацию",
      suspend: "Приостановить",
      disable: "Выключить",
      enable: "Включить",
      delete: "Удалить",
      servicesKicker: "Сервисы",
      servicesTitle: "Управление сервисами",
      port: "Порт",
      portUnset: "Порт не задан",
      description: "Описание",
      createService: "Создать сервис",
      roundsKicker: "Раунды",
      roundsTitle: "Жизненный цикл соревнования",
      nextSuggestedRound: "Следующий рекомендуемый раунд: {number}",
      runningRoundReady: "Раунд {number} готов к checker tick",
      noRunningRound: "Сейчас нет запущенного раунда для checker tick",
      lastCheckerReport: "Последний отчёт чекера: {date}",
      noCheckerReport: "Для активного раунда пока нет отчёта чекера.",
      runCheckerTick: "Запустить checker tick",
      roundNumber: "Номер раунда",
      scheduleCount: "Количество в батче",
      scheduleStart: "Старт расписания",
      createPlannedRound: "Создать запланированный раунд",
      scheduleBatch: "Запланировать пакет раундов",
      start: "Запустить",
      finish: "Завершить",
      generateFlags: "Сгенерировать флаги",
      serviceGeneratedFlags: "{count} сгенер. флагов",
      teamMeta: "{count} участн. · {moderation}",
      roundGeneratedFlags: "{count} флагов сгенерировано",
      working: "Выполняется..."
    },
    prompts: {
      removeMember: 'Удалить "{username}" из команды?',
      deleteTeam: 'Удалить команду "{name}"? Это удалит и связанные соревновательные данные.',
      deleteService: 'Удалить сервис "{name}"?',
      moderationNote: 'Заметка модерации для "{name}"',
      rejectReservation: 'Причина отклонения для "{name}"'
    },
    messages: {
      signedInAs: "Вход выполнен как {username}.",
      sessionClosed: "Сессия завершена.",
      teamRegistered: "Регистрация команды завершена.",
      reservationCreated: "Заявка на резервирование имени команды создана.",
      teamProfileUpdated: "Профиль команды обновлён.",
      teamMemberAdded: "Участник добавлен в команду.",
      memberRoleUpdated: "Роль участника обновлена.",
      memberRemoved: "Участник удалён.",
      flagSubmitted: "Флаг отправлен.",
      adminActionCompleted: "Админ-действие выполнено.",
      teamCreated: "Команда создана.",
      teamUpdated: "Команда обновлена.",
      serviceCreated: "Сервис создан.",
      serviceUpdated: "Сервис обновлён.",
      roundCreated: "Запланированный раунд создан.",
      roundStarted: "Раунд запущен.",
      roundFinished: "Раунд завершён.",
      flagsGenerated: "Флаги сгенерированы.",
      checkerTickCompleted: "Цикл checker завершён.",
      competitionSettingsUpdated: "Настройки соревнования обновлены.",
      roundsScheduled: "Пакет раундов запланирован.",
      reservationApproved: "Резервирование одобрено.",
      reservationRejected: "Резервирование отклонено.",
      authRestoreFailed: "Не удалось восстановить сессию.",
      dashboardLoadFailed: "Не удалось загрузить дашборд BaltCTF.",
      servicesLoadFailed: "Не удалось загрузить матрицу статусов сервисов.",
      registrationSettingsFailed: "Не удалось загрузить настройки регистрации.",
      loginFailed: "Не удалось выполнить вход.",
      registerFailed: "Не удалось зарегистрировать команду.",
      reservationFailed: "Не удалось создать заявку на резервирование.",
      flagSubmitFailed: "Не удалось отправить флаг.",
      teamProfileFailed: "Не удалось обновить профиль команды.",
      addMemberFailed: "Не удалось добавить участника.",
      updateRoleFailed: "Не удалось обновить роль участника.",
      removeMemberFailed: "Не удалось удалить участника.",
      adminStateFailed: "Не удалось загрузить состояние админки.",
      adminActionFailed: "Не удалось выполнить админ-действие."
    }
  }
};

function getMessage(locale, key) {
  return key.split(".").reduce((accumulator, segment) => {
    if (accumulator && typeof accumulator === "object") {
      return accumulator[segment];
    }
    return undefined;
  }, messages[locale]);
}

function interpolate(template, params = {}) {
  if (typeof template !== "string") {
    return "";
  }

  return template.replace(/\{(\w+)\}/g, (match, key) => {
    if (params[key] === undefined || params[key] === null) {
      return match;
    }
    return String(params[key]);
  });
}

export function setLanguage(language) {
  currentLanguage.value = language === "ru" ? "ru" : "en";
  try {
    window.localStorage.setItem(LANGUAGE_STORAGE_KEY, currentLanguage.value);
  } catch {
    return;
  }
}

export function translate(key, params = {}) {
  const template =
    getMessage(currentLanguage.value, key) ??
    getMessage("en", key) ??
    key;

  return interpolate(template, params);
}

export function formatLocalizedDateTime(value) {
  if (!value) {
    return translate("common.noData");
  }

  return new Intl.DateTimeFormat(currentLanguage.value === "ru" ? "ru-RU" : "en-GB", {
    dateStyle: "medium",
    timeStyle: "short"
  }).format(new Date(value));
}

export function useI18n() {
  return {
    currentLanguage,
    languageOptions,
    setLanguage,
    t: translate,
    formatDateTime: formatLocalizedDateTime
  };
}
