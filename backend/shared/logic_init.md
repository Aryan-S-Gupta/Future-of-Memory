# 🟢 home page visited

## views.py

- **create_session()** -> create a new Session -> return session_id -> frontend stores it

# 🟢 start button clicked -> static background page visited

## views.py

- **build_next_turn_asset(session_id, year)** -> starts quesiton generation + image generation + scenario generation -> return turn_id -> frontend stores it

	- **generate_and_save_question()** -> LLM generates 1 question with 4 options, creates 1 Turn, 4 Options -> return turn_id

	- **[bg job] start_prerender_jobs()** -> *this takes time and runs in the bg, not sure how long*

		- [queue_llm, job 1] generate_image_text() -> LLM generates 4 image_text, update Option.image_text in DB

		- [queue_image, job 1, enqueue at the end of generate_image_text] generate_four_images_blocking() -> ComfyUI generates 4 images, creates 4 ImageRender

		- [queue_llm, job 2, this can enqueue in generate_image_text as well so that it is processed in parallel with image_generation] generate_scenario(session_id, turn_id, year) -> for each one of the option, LLM generates a scenario, update Option.scenario_text

# 🟢 continue button clicked -> question page visited (timer + chatroom? needs to give sufficient time to generation jobs!)

## views.py

- **question_display(session_id, turn_id, year)** -> return question json from DB

	- from DB return Turn.question + Option.id + Option.option_text

# 🟢 a final choice made -> display page visited

## views.py

- **display_scenario_and_image(session_id, turn_id, option_id)** -> return scenario_text + image_status + image_path

	- upate Turn.user_choice, from DB return Option.scenario_text

	- **display_by_option(session_id, turn_id, option_id)** -> finds the ImageRender for this option_id -> from DB return status + image path

- **build_next_turn_asset(session_id, year)** -> starts quesiton generation + image generation + scenario generation -> return turn_id -> frontend stores it

	- **generate_and_save_question()** -> LLM generates 1 question with 4 options, creates 1 Turn, 4 Options -> return turn_id

	- **[bg job] start_prerender_jobs()** -> *this takes time and runs in the bg, not sure how long*

		- [queue_llm, job 1] generate_image_text() -> LLM generates 4 image_text, update Option.image_text in DB

		- [queue_image, job 1] generate_four_images_blocking() -> ComfyUI generates 4 images, creates 4 ImageRender

		- [queue_llm, job 2, this can enqueue in generate_image_text as well so that it is processed in parallel with image_generation] generate_scenario(session_id, turn_id, year) -> for each one of the option, LLM generates a scenario, update Option.scenario_text

# 🟢 continue button clicked -> question page visited

## views.py

- **question_display(session_id, turn_id, year)** -> return question json from DB, starts scenario generation (for each option)

	- from DB return Turn.question + Option.id + Option.option_text