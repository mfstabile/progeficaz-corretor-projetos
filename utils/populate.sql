INSERT INTO `twtester`.`projects` (`project_name`, `corrector_class`, `date_from`, `date_to`) VALUES ('Projeto1A', 'Projeto1A', NOW(), NOW());

INSERT INTO `twtester`.`tasks` (`task_name`, `project_name`, `corrector_method`) VALUES ('Handout', 'Projeto1A', 'test_handout');
INSERT INTO `twtester`.`tasks` (`task_name`, `project_name`, `corrector_method`) VALUES ('Persistência de dados', 'Projeto1A', 'test_persistency');
INSERT INTO `twtester`.`tasks` (`task_name`, `project_name`, `corrector_method`) VALUES ('Apagar anotações', 'Projeto1A', 'test_delete');
INSERT INTO `twtester`.`tasks` (`task_name`, `project_name`, `corrector_method`) VALUES ('Editar anotações', 'Projeto1A', 'test_edit');
