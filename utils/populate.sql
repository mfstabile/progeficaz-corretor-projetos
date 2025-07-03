INSERT INTO `twtester`.`projects` (`project_name`, `corrector_class`, `date_from`, `date_to`) VALUES ('Projeto1', 'Projeto1', NOW(), NOW());

INSERT INTO `twtester`.`tasks` (`task_name`, `project_name`, `corrector_method`) VALUES ('Handout', 'Projeto1', 'test_handout');
INSERT INTO `twtester`.`tasks` (`task_name`, `project_name`, `corrector_method`) VALUES ('Persistência de dados', 'Projeto1', 'test_persistency');
INSERT INTO `twtester`.`tasks` (`task_name`, `project_name`, `corrector_method`) VALUES ('Apagar anotações', 'Projeto1', 'test_delete');
INSERT INTO `twtester`.`tasks` (`task_name`, `project_name`, `corrector_method`) VALUES ('Editar anotações', 'Projeto1', 'test_edit');
INSERT INTO `twtester`.`tasks` (`task_name`, `project_name`, `corrector_method`) VALUES ('Favoritar anotações', 'Projeto1', 'test_favorite');
INSERT INTO `twtester`.`tasks` (`task_name`, `project_name`, `corrector_method`) VALUES ('Sistema de tags', 'Projeto1', 'test_tags');
