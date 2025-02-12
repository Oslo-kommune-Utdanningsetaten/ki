# Bot

- [ ] Relation name: `model_id` → `model`
- [ ] Rename db field: `img_bot` → `is_image_bot`
- [ ] Rename db field: `library` → `is_library_bot`
- [ ] Rename db field: `mandatory` → `is_mandatory`
- [ ] Rename db field: `prompt_visibility` → `is_prompt_visibile`
- [ ] Rename db field: `allow_distribution` → `is_distribution_allowed`

# BotModel

- [ ] Primary key: `model_id` → `id`
- [ ] Rename db field: `deployment_id` → `deployment_key`

# Setting

- [ ] Add primary key (autofield): `id`
- [ ] Add unique constraint to `setting_key`

# Favorite

- [ ] Relation name: `bot_id` → `bot`
- [ ] Rename db field: `user_id` → `feide_user`

# PromptChoice

- [ ] Relation name: `bot_id` → `bot`

# ChoiceOption

- [ ] Relation name: `choice_id` → `choice`

# School

- [ ] Add primary key (autofield): `id`
- [ ] Add unique constraint to: `org_nr`

# BotAccess

- [ ] Primary key: `access_id` → `id`
- [ ] Relation name: `bot_id` → `bot`
- [ ] Relation name: `school_id` → `school`

# BotLevel

- [ ] Primary key: `level_id` → `id`
- [ ] Relation name: `access_id` → `bot_access`

# SchoolAccess

- [ ] Primary key: `access_id` → `id`
- [ ] Relation name: `school_id` → `school`

# SubjectAccess

- [ ] Relation name: `bot_id` → `bot`
- [ ] Rename db field: `created` → `created_at`

# PageText

- [ ] Primary key: `page_id` → `id`
- [ ] Rename db field: `page_title` → `title`
- [ ] Rename db field: `page_text` → `text`
- [ ] Rename db field: `public` → `is_public`

# Role

- [ ] Add primary key (autofield): `id`
- [ ] Rename db field: `user_id` → `feide_user`
- [ ] Add unique constraint to `feide_user`

# LogSchool

- [ ] Rename db field: `school` → `school_id`
- [ ] Relation name: `log_id` → `log`
- [ ] Relation name: `school_id` → `school`

# TagCategory

- [ ] Primary key: `category_id` → `id`
- [ ] Rename db field: `category_name` → `name`
- [ ] Rename db field: `category_order` → `order`

# TagLabel

- [ ] Primary key: `tag_label_id` → `id`
- [ ] Rename db field: `tag_label_name` → `name`
- [ ] Rename db field: `tag_label_order` → `order`
- [ ] Relation name: `category_id` → `category`4

# Tag

- [ ] Primary key: `tag_id` → `id`
- [ ] Rename db field: `tag_value` → `value`
- [ ] Relation name: `category_id` → `category`
- [ ] Relation name: `bot_id` → `bot`
