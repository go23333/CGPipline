# -*- coding: utf-8 -*-

import os

import maya.cmds as cmds

from zynn_check.core.check import Check, register


@register
class AudioExist(Check):
    name = 'audio_exist'
    label = u"音频存在"
    category = u"音频"
    check_type = 'scene'
    result_type = 'text'
    stages = ['layout', 'animation']
    requires = ['lens_file_name']

    def run(self):
        audios = cmds.ls(type='audio') or []
        if not audios:
            self.errors.append(u"场景中缺少音频")
            return

        if len(audios) > 1:
            self.errors.append(u"场景中存在多个音频")
            return

        lens_name = self.file_info.get_lens_name()
        audio_name = lens_name[6:]
        if audios[0] != audio_name:
            self.errors.append(u"音频不正确：{}".format(audio_name))

        self.context['shared']['audio'] = audios[0]

    def fix(self, errors=None):
        audios = cmds.ls(type='audio') or []
        cmds.delete(audios)

        project_name = self.file_info.get_project()
        lens_name = self.file_info.get_lens_name()
        episode, scene, lens = lens_name.split('_')
        audio_path = 'Y:/{}/{}/Animatic/Sound/{}/{}_{}.wav'.format(
            project_name, episode.upper(), scene, scene, lens
        )

        if not os.path.exists(audio_path):
            audio_path = 'Y:/{}/{}/Animatic/Sound/{}/{}_{}.wav'.format(
                project_name, episode.capitalize()(), scene, scene, lens
            )

        cmds.sound(file=audio_path, name='{}_{}'.format(scene, lens))


@register
class AudioPath(Check):
    name = 'audio_path'
    label = u"音频路径"
    category = u"音频"
    check_type = 'scene'
    result_type = 'node'
    stages = ['layout', 'animation']
    requires = ['audio_exist']

    def run(self):
        audio = self.context['shared'].get('audio')
        if not audio:
            return

        project_name = self.file_info.get_project()
        lens_name = self.file_info.get_lens_name()
        episode, scene, lens = lens_name.split('_')
        audio_path = cmds.getAttr(audio + '.filename')
        should_audio_path = 'Y:/{}/{}/Animatic/Sound/{}/{}_{}.wav'.format(
            project_name, episode, scene, scene, lens
        )
        if audio_path.lower() != should_audio_path.lower():
            self.errors.append(audio)

    def fix(self, errors=None):
        errors = self.selectable() if errors is None else errors

        project_name = self.file_info.get_project()
        lens_name = self.file_info.get_lens_name()
        episode, scene, lens = lens_name.split('_')

        audio_path = 'Y:/{}/{}/Animatic/Sound/{}/{}_{}.wav'.format(
            project_name, episode.upper(), scene, scene, lens
        )
        if not os.path.exists(audio_path):
            audio_path = 'Y:/{}/{}/Animatic/Sound/{}/{}_{}.wav'.format(
                project_name, episode.capitalize()(), scene, scene, lens
            )

        cmds.setAttr(errors[0] + '.filename', audio_path, type='string')


@register
class AudioStartFrame(Check):
    name = 'audio_start_frame'
    label = u"音频起始帧"
    category = u"音频"
    check_type = 'scene'
    result_type = 'node'
    stages = ['layout', 'animation']
    requires = ['audio_exist']

    def run(self):
        audio = self.context['shared'].get('audio')
        if not audio:
            return

        start_frame = cmds.getAttr(audio + '.offset')
        should_start_frame = 1.0
        if self.file_info.get_project() == u'EMFZ_TWO':
            should_start_frame = 101.0
        if start_frame != should_start_frame:
            self.errors.append(audio)

    def fix(self, errors=None):
        errors = self.selectable() if errors is None else errors
        should_start_frame = 1.0
        if self.file_info.get_project() == u'EMFZ_TWO':
            should_start_frame = 101.0
        cmds.setAttr(errors[0] + '.offset', should_start_frame)


@register
class AudioDuration(Check):
    name = 'audio_duration'
    label = u"音频帧数"
    category = u"音频"
    check_type = 'scene'
    result_type = 'text'
    stages = ['layout', 'animation']
    requires = ['audio_exist', 'camera_start_frame']

    def run(self):
        audio = self.context['shared'].get('audio')
        camera = self.context['shared'].get('main_camera_transform')
        if not audio:
            return

        audio_duration = int(round(cmds.getAttr(audio + '.duration')))
        camera_split = camera.split('_')
        camera_duration = int(camera_split[4]) - int(camera_split[3]) + 1

        if audio_duration != camera_duration:
            self.errors.append(audio)

    def fix(self, errors=None):
        errors = self.selectable() if errors is None else errors
        audio_duration = int(round(cmds.getAttr(errors[0] + '.duration')))

        camera = self.context['shared'].get('main_camera_transform')
        camera_split = camera.split('_')
        camera_split[4] = '{:03d}'.format(int(camera_split[3]) + audio_duration - 1)
        new_camera_name = '_'.join(camera_split)
        cmds.rename(camera, new_camera_name)
        self.context['shared']['main_camera_transform'] = new_camera_name
        self.context['shared']['main_camera_shape'] = new_camera_name + 'Shape'

        cmds.playbackOptions(ast=int(camera_split[3]), aet=int(camera_split[4]))
        cmds.playbackOptions(min=int(camera_split[3]), max=int(camera_split[4]))
